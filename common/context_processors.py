def sidebar_permissions(request):
    user = request.user
    if not user.is_authenticated:
        return {}

    is_super = user.is_superuser

    # ---------------- SETUP ----------------
    setup_children = {
        "client": is_super or user.has_perm("setup.view_client"),
        "contractor_type": is_super or user.has_perm("setup.view_contractortype"),
        "contractor": is_super or user.has_perm("setup.view_contractor"),
        "project_role": is_super or user.has_perm("setup.view_projectrole"),
        "work_category": is_super or user.has_perm("setup.view_workcategory"),
        "authority": is_super or user.has_perm("setup.view_authority"),
    }

    # ---------------- RESOURCES ----------------
    resources_children = {
        "equipment": is_super or user.has_perm("resources.view_equipment"),
        "manpower": is_super or user.has_perm("resources.view_manpower"),
    }

    # ---------------- FINANCE ----------------
    finance_children = {
        "payment_certificate": is_super or user.has_perm("finance.view_paymentcertificate"),
        "fund_transaction": is_super or user.has_perm("finance.view_fundtransaction"),
    }

    # ---------------- QUALITY ----------------
    quality_children = {
        "material_test": is_super or user.has_perm("quality.view_materialtest"),
        "work_approval": is_super or user.has_perm("quality.view_workapproval"),
    }

    # ---------------- SITE MANAGEMENT ----------------
    sitemanage_children = {
        "overview": is_super or user.has_perm("sitemanage.access_sitemanage"),
        "activity": is_super or user.has_perm("sitemanage.view_activity"),
        "visitor": is_super or user.has_perm("sitemanage.view_sitevisitor"),
        "photos": is_super or user.has_perm("sitemanage.view_projectimage"),
    }

    # ---------------- REPORTS ----------------
    reports_children = {
        "project": is_super or user.has_perm("reports.view_projectreport"),
        "progress_cover": is_super or user.has_perm("reports.view_progressreportcover"),
        "progress": is_super or user.has_perm("reports.view_projectreport"),
        "finance": is_super or user.has_perm("reports.view_financereport"),
        "quality": is_super or user.has_perm("reports.view_qualityreport"),
        "resources": is_super or user.has_perm("reports.view_resourcesreport"),
    }

    # ---------------- MAIN SIDEBAR ----------------
    sidebar_perms = {
        "dashboard": is_super or user.has_perm("accounts.view_dashboard"),
        "projects": is_super or user.has_perm("projects.view_project"),
        "resources": any(resources_children.values()),
        "finance": any(finance_children.values()),
        "quality": any(quality_children.values()),
        "sitemanage": any(sitemanage_children.values()),
        "reports": any(reports_children.values()),
        "compliance": is_super or user.has_perm("compliance.view_compliance"),
        "setup": any(setup_children.values()),
    }

    # ---------------- ACTIVE PARENT ----------------
    current_app = getattr(request.resolver_match, "app_name", "")

    active_parent = {
        "dashboard": current_app == "dashboard",
        "projects": current_app == "projects",
        "resources": current_app == "resources",
        "finance": current_app == "finance",
        "quality": current_app == "quality",
        "sitemanage": current_app == "sitemanage",
        "reports": current_app == "reports",
        "compliance": current_app == "compliance",
        "setup": current_app == "setup",
    }

    return {
        "sidebar_perms": sidebar_perms,
        "resources_children": resources_children,
        "finance_children": finance_children,
        "quality_children": quality_children,
        "sitemanage_children": sitemanage_children,
        "reports_children": reports_children,
        "setup_children": setup_children,
        "active_parent": active_parent,
    }


