/** @odoo-module **/

/**
 * KPI Widget Components for Saudi ERP Dashboard
 */

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class KpiCard extends Component {
    static template = "saudi_erp_dashboard.KpiCard";
    static props = {
        title: String,
        titleAr: { type: String, optional: true },
        value: [String, Number],
        subtitle: { type: String, optional: true },
        icon: String,
        color: { type: String, default: "green" },
        badge: { type: String, optional: true },
        badgeType: { type: String, optional: true },
        onClick: { type: Function, optional: true },
    };
}

export class AlertBanner extends Component {
    static template = "saudi_erp_dashboard.AlertBanner";
    static props = {
        type: String, // danger, warning, info
        icon: String,
        title: String,
        description: String,
        actionLabel: { type: String, optional: true },
        onAction: { type: Function, optional: true },
    };
}
