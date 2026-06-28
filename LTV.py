def run_portfolio_ltv(loans, fmv_sources):
    policy      = get_policy_dict()
    fmv_sources = [s for s in fmv_sources if 'id' in s]
    fmv_id_set  = {s['id'] for s in fmv_sources}

    def is_exempt(loan):
        return _loan_is_ltv_exempt(loan)

    collateral_fmv_map = {s['id']: s['Amount'] for s in fmv_sources}
    total_fmv          = sum(s['Amount'] for s in fmv_sources)

    # ── Separate loans by mode (preserve insertion order) ──
    pool_loans     = [l for l in loans if not is_exempt(l) and l.get('collateral_mode', 'pool') == 'pool' and policy.get(l['Loan Type']) is not None]
    assigned_loans = [l for l in loans if not is_exempt(l) and l.get('collateral_mode') == 'assigned' and bool(l.get('assigned_collateral_ids')) and policy.get(l['Loan Type']) is not None]

    # ── Determine which collateral IDs are dedicated (assigned) ──
    assigned_collateral_ids = set()
    for loan in assigned_loans:
        for cid in loan.get('assigned_collateral_ids', []):
            if cid in fmv_id_set:
                assigned_collateral_ids.add(cid)

    pool_collateral_ids = fmv_id_set - assigned_collateral_ids
    pool_fmv            = sum(collateral_fmv_map.get(cid, 0.0) for cid in pool_collateral_ids)

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 1: figure out which group was added FIRST — pool or assigned.
    #         We look at the earliest _loan_id in each group.
    # ─────────────────────────────────────────────────────────────────────────
    first_pool_id     = min((l['_loan_id'] for l in pool_loans),     default=float('inf'))
    first_assigned_id = min((l['_loan_id'] for l in assigned_loans), default=float('inf'))
    pool_first        = first_pool_id <= first_assigned_id   # True → pool entered before assigned

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 2: Build a remaining-FMV tracker per collateral ID.
    #         Assigned loans each have their own collateral; pool loans share
    #         the pool collateral IDs.  We track how much FMV is still free.
    # ─────────────────────────────────────────────────────────────────────────
    remaining_fmv = {sid: collateral_fmv_map[sid] for sid in fmv_id_set}

    # Allocation stores: {_loan_id: {"cid": allocated_amount, ...}}
    pool_alloc_detail     = {}   # for pool loans
    assigned_alloc_detail = {}   # for assigned loans

    # ─────────────────────────────────────────────────────────────────────────
    # Helper — allocate pool FMV for a single pool loan.
    # Pool loans use ALL pool-collateral IDs collectively; we deduct from each
    # proportionally so that remaining_fmv stays consistent.
    # LTV for pool loan = principal / current total pool FMV remaining
    # ─────────────────────────────────────────────────────────────────────────
    def _allocate_pool(loan):
        lid          = loan['_loan_id']
        principal    = loan['Principal']
        max_ltv      = policy.get(loan['Loan Type'])
        current_pool = sum(remaining_fmv.get(cid, 0.0) for cid in pool_collateral_ids)

        if current_pool <= 0:
            pool_alloc_detail[lid] = {}
            return

        # How much FMV does this loan "consume" (i.e. the required FMV at max LTV)?
        req_fmv   = principal / (max_ltv / 100.0)
        allocated = min(req_fmv, current_pool)

        # Deduct from each pool collateral proportionally
        alloc_map = {}
        for cid in pool_collateral_ids:
            proportion         = remaining_fmv.get(cid, 0.0) / current_pool if current_pool > 0 else 0.0
            deduct             = allocated * proportion
            remaining_fmv[cid] = max(0.0, remaining_fmv.get(cid, 0.0) - deduct)
            alloc_map[cid]     = deduct

        pool_alloc_detail[lid] = alloc_map

    # ─────────────────────────────────────────────────────────────────────────
    # Helper — allocate dedicated FMV for a single assigned loan.
    # Assigned loans use their specific collateral IDs only.
    # LTV = principal / (specific collateral FMV - already allocated for pool)
    # "already allocated for pool" means whatever was deducted from remaining_fmv
    # before this assigned loan was processed.
    # ─────────────────────────────────────────────────────────────────────────
    def _allocate_assigned(loan):
        lid       = loan['_loan_id']
        principal = loan['Principal']
        max_ltv   = policy.get(loan['Loan Type'])
        cids      = [c for c in loan.get('assigned_collateral_ids', []) if c in fmv_id_set]

        if not cids:
            assigned_alloc_detail[lid] = {}
            return

        # Available FMV on the specific collaterals (after any prior pool deductions)
        available = sum(remaining_fmv.get(cid, 0.0) for cid in cids)

        if available <= 0:
            assigned_alloc_detail[lid] = {}
            return

        req_fmv   = principal / (max_ltv / 100.0)
        allocated = min(req_fmv, available)

        # Deduct from each specific collateral proportionally
        alloc_map = {}
        for cid in cids:
            proportion         = remaining_fmv.get(cid, 0.0) / available if available > 0 else 0.0
            deduct             = allocated * proportion
            remaining_fmv[cid] = max(0.0, remaining_fmv.get(cid, 0.0) - deduct)
            alloc_map[cid]     = deduct

        assigned_alloc_detail[lid] = alloc_map

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 3: Process in the correct order based on which group came first.
    #         Within each group, preserve insertion order.
    # ─────────────────────────────────────────────────────────────────────────
    # We interleave by _loan_id order so that if someone adds pool, then
    # assigned, then pool again, the ordering is respected faithfully.
    # ─────────────────────────────────────────────────────────────────────────
    non_exempt_active = [
        l for l in loans
        if not is_exempt(l)
        and policy.get(l['Loan Type']) is not None
        and (
            l.get('collateral_mode', 'pool') == 'pool'
            or (l.get('collateral_mode') == 'assigned' and bool(l.get('assigned_collateral_ids')))
        )
    ]
    # Already in insertion order (loans list preserves order)

    for loan in non_exempt_active:
        mode = loan.get('collateral_mode', 'pool')
        if mode == 'pool':
            _allocate_pool(loan)
        else:
            _allocate_assigned(loan)

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 4: Compute per-loan LTV results
    # ─────────────────────────────────────────────────────────────────────────
    # For LTV display:
    #   Pool loan   → LTV = principal / total_current_pool_fmv_at_time_of_allocation
    #                 But we need the "effective FMV" = sum of what was available to it.
    #                 We'll reconstruct: effective_fmv = sum(alloc_map values) * (max_ltv/100) / principal
    #                 Actually simpler: effective_fmv_available = allocated / (max_ltv/100) ... no.
    #
    # Per user spec:
    #   Pool LTV   = loan / total FMV  (full pool FMV, i.e. sum of pool collateral original FMV)
    #   Assigned   = loan / (specific collateral FMV - already allocated for pool)
    #
    # So we just need:
    #   pool_loan_fmv_denominator      = pool_fmv  (the original total pool FMV)
    #   assigned_loan_fmv_denominator  = sum(remaining_fmv[cid] before assignment + allocated)
    #                                  = sum of remaining_fmv at time of processing (before deduction)
    #
    # The cleanest approach: record the available FMV at the moment each loan is processed.
    # Let's redo with a snapshot approach.
    # ─────────────────────────────────────────────────────────────────────────

    # Reset and redo with snapshots
    remaining_fmv2    = {sid: collateral_fmv_map[sid] for sid in fmv_id_set}
    loan_effective_fmv = {}   # {_loan_id: effective_fmv_denominator}
    pool_alloc_detail2 = {}
    assigned_alloc_detail2 = {}

    def _allocate_pool2(loan):
        lid       = loan['_loan_id']
        principal = loan['Principal']
        max_ltv   = policy.get(loan['Loan Type'])

        # Per spec: pool LTV = loan / total_pool_fmv (original full pool FMV)
        current_pool_original = pool_fmv   # always the full original pool FMV

        if current_pool_original <= 0:
            pool_alloc_detail2[lid]   = {}
            loan_effective_fmv[lid]   = 0.0
            return

        # Snapshot available before deduction
        current_available = sum(remaining_fmv2.get(cid, 0.0) for cid in pool_collateral_ids)

        req_fmv   = principal / (max_ltv / 100.0)
        allocated = min(req_fmv, current_available)

        alloc_map = {}
        if current_available > 0:
            for cid in pool_collateral_ids:
                proportion          = remaining_fmv2.get(cid, 0.0) / current_available
                deduct              = allocated * proportion
                remaining_fmv2[cid] = max(0.0, remaining_fmv2.get(cid, 0.0) - deduct)
                alloc_map[cid]      = deduct

        pool_alloc_detail2[lid] = alloc_map
        # Effective FMV denominator for LTV: full pool FMV as per spec
        loan_effective_fmv[lid] = current_pool_original

    def _allocate_assigned2(loan):
        lid       = loan['_loan_id']
        principal = loan['Principal']
        max_ltv   = policy.get(loan['Loan Type'])
        cids      = [c for c in loan.get('assigned_collateral_ids', []) if c in fmv_id_set]

        if not cids:
            assigned_alloc_detail2[lid] = {}
            loan_effective_fmv[lid]     = 0.0
            return

        # Per spec: assigned LTV = loan / (specific collateral FMV - already allocated for pool)
        # "specific collateral FMV - already allocated" = remaining_fmv2 at this point
        available = sum(remaining_fmv2.get(cid, 0.0) for cid in cids)

        if available <= 0:
            assigned_alloc_detail2[lid] = {}
            loan_effective_fmv[lid]     = 0.0
            return

        req_fmv   = principal / (max_ltv / 100.0)
        allocated = min(req_fmv, available)

        alloc_map = {}
        for cid in cids:
            proportion          = remaining_fmv2.get(cid, 0.0) / available if available > 0 else 0.0
            deduct              = allocated * proportion
            remaining_fmv2[cid] = max(0.0, remaining_fmv2.get(cid, 0.0) - deduct)
            alloc_map[cid]      = deduct

        assigned_alloc_detail2[lid] = alloc_map
        # Effective FMV denominator = available before deduction (specific - already allocated)
        loan_effective_fmv[lid] = available

    for loan in non_exempt_active:
        mode = loan.get('collateral_mode', 'pool')
        if mode == 'pool':
            _allocate_pool2(loan)
        else:
            _allocate_assigned2(loan)

    # Remaining pool after all allocations
    remaining_pool_fmv = sum(remaining_fmv2.get(cid, 0.0) for cid in pool_collateral_ids)

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 5: Build result rows
    # ─────────────────────────────────────────────────────────────────────────
    collateral_usage = {s['id']: [] for s in fmv_sources}
    for loan in assigned_loans:
        for cid in loan.get('assigned_collateral_ids', []):
            if cid in collateral_usage:
                collateral_usage[cid].append(loan['_loan_id'])

    results = []

    for loan in loans:
        lid       = loan['_loan_id']
        lt        = loan['Loan Type']
        principal = loan['Principal']
        mode      = loan.get('collateral_mode', 'pool')
        exempt    = is_exempt(loan)
        max_ltv   = policy.get(lt)

        # Determine exempt reason
        exempt_reason = None
        if max_ltv is None:
            exempt_reason = "policy"
        elif loan.get('override_ltv', False):
            exempt_reason = "override"
        elif loan.get('tied_property_ids') and not (
            mode == 'assigned' and bool(loan.get('assigned_collateral_ids'))
        ):
            exempt_reason = "tieup"

        if exempt:
            results.append({
                **loan,
                'Max LTV%': None, 'Assigned FMV': 0.0, 'Pool FMV': 0.0,
                'Total FMV': 0.0, 'LTV%': None, 'Pass_Status': True,
                'Is_Unsecured': True, 'Collateral_Mode': mode,
                'Collateral_Names': [], 'Shared_Collateral_Ids': [],
                'No_FMV_Error': False, 'Exempt_Reason': exempt_reason,
            })
            continue

        effective_fmv = loan_effective_fmv.get(lid, 0.0)

        if mode == 'pool':
            assigned_fmv_val = 0.0
            pool_fmv_val     = effective_fmv   # full pool FMV for display
            total_alloc      = effective_fmv
        else:
            # Assigned: show the specific collateral's available FMV
            assigned_fmv_val = effective_fmv
            pool_fmv_val     = 0.0
            total_alloc      = effective_fmv

        if total_alloc <= 0:
            ltv_pct      = None
            passes       = False
            no_fmv_error = True
        else:
            ltv_pct      = principal / total_alloc * 100.0
            passes       = ltv_pct <= max_ltv
            no_fmv_error = False

        assigned_coll_names = _get_collateral_names(
            loan.get('assigned_collateral_ids', []), fmv_sources
        )
        shared_cids = [
            cid for cid in loan.get('assigned_collateral_ids', [])
            if len(collateral_usage.get(cid, [])) > 1
        ]

        results.append({
            **loan,
            'Max LTV%': max_ltv,
            'Assigned FMV': assigned_fmv_val,
            'Pool FMV': pool_fmv_val,
            'Total FMV': total_alloc,
            'LTV%': ltv_pct,
            'Pass_Status': passes,
            'Is_Unsecured': False,
            'Collateral_Mode': mode,
            'Collateral_Names': assigned_coll_names,
            'Shared_Collateral_Ids': shared_cids,
            'No_FMV_Error': no_fmv_error,
            'Exempt_Reason': None,
        })

    secured_results         = [r for r in results if not r['Is_Unsecured']]
    total_secured_principal = sum(r['Principal'] for r in secured_results)
    total_exposure          = sum(r['Principal'] for r in results)
    total_alloc_fmv         = sum(r['Total FMV'] for r in secured_results)
    wtd_ltv = (
        total_secured_principal / total_alloc_fmv * 100.0
        if total_alloc_fmv > 0 else 0.0
    )
    aggregate_ltv = (
        total_secured_principal / total_fmv * 100.0 if total_fmv > 0 else 0.0
    )
    overall_pass = all(r['Pass_Status'] for r in results)

    return results, {
        'total_fmv': total_fmv,
        'pool_fmv': pool_fmv,
        'remaining_pool': remaining_pool_fmv,
        'total_exposure': total_exposure,
        'total_secured_principal': total_secured_principal,
        'total_alloc_fmv': total_alloc_fmv,
        'wtd_ltv': wtd_ltv,
        'aggregate_ltv': aggregate_ltv,
        'overall_pass': overall_pass,
        'collateral_usage': collateral_usage,
        'assigned_collateral_ids': assigned_collateral_ids,
        'pool_collateral_ids': pool_collateral_ids,
    }
