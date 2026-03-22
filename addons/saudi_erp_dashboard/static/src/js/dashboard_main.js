/** @odoo-module **/

/**
 * Saudi ERP - Main Dashboard Controller
 * Custom admin dashboard replacing Odoo default backend
 */

import { Component, useState, onWillStart, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { formatMonetary } from "@web/views/fields/formatters";

export class SaudiDashboard extends Component {
    static template = "saudi_erp_dashboard.MainDashboard";

    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.notification = useService("notification");

        this.state = useState({
            loading: true,
            data: null,
            recentInvoices: [],
            currentLang: 'en',
            sidebarCollapsed: false,
        });

        onWillStart(async () => {
            await this._loadDashboardData();
        });
    }

    async _loadDashboardData() {
        try {
            const [dashData, invoices] = await Promise.all([
                this.rpc("/saudi_erp/dashboard/data", {}),
                this.rpc("/saudi_erp/dashboard/recent_invoices", { limit: 8 }),
            ]);
            this.state.data = dashData;
            this.state.recentInvoices = invoices;
        } catch (e) {
            console.error("Dashboard load error:", e);
            this.notification.add("Failed to load dashboard data", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    get formattedRevenue() {
        if (!this.state.data) return "0.00";
        const amount = this.state.data.kpis.revenue_month;
        return new Intl.NumberFormat('en-SA', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    }

    get formattedVAT() {
        if (!this.state.data) return "0.00";
        return new Intl.NumberFormat('en-SA', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(this.state.data.kpis.vat_month);
    }

    get revenueGrowthClass() {
        if (!this.state.data) return "neutral";
        const g = this.state.data.kpis.revenue_growth;
        return g > 0 ? "up" : g < 0 ? "down" : "neutral";
    }

    get revenueGrowthIcon() {
        if (!this.state.data) return "→";
        const g = this.state.data.kpis.revenue_growth;
        return g > 0 ? "↑" : g < 0 ? "↓" : "→";
    }

    get zatcaStatusClass() {
        if (!this.state.data) return "not_registered";
        return this.state.data.company.zatca_status || "not_registered";
    }

    get zatcaStatusLabel() {
        const labels = {
            "not_registered": "Not Registered",
            "phase1": "Phase 1 - Generation",
            "phase2": "Phase 2 - Integrated",
        };
        return labels[this.zatcaStatusClass] || "Unknown";
    }

    toggleSidebar() {
        this.state.sidebarCollapsed = !this.state.sidebarCollapsed;
    }

    toggleLanguage() {
        this.state.currentLang = this.state.currentLang === 'en' ? 'ar' : 'en';
        document.documentElement.dir = this.state.currentLang === 'ar' ? 'rtl' : 'ltr';
    }

    async refreshData() {
        this.state.loading = true;
        await this._loadDashboardData();
    }

    navigateTo(actionXmlId) {
        this.action.doAction(actionXmlId);
    }

    getPaymentStateBadge(state) {
        const map = {
            'paid': 'paid',
            'partial': 'pending',
            'not_paid': 'overdue',
            'in_payment': 'pending',
        };
        return map[state] || 'draft';
    }

    getZatcaBadge(status) {
        const map = {
            'not_submitted': 'draft',
            'submitted': 'pending',
            'accepted': 'paid',
            'cleared': 'cleared',
            'rejected': 'overdue',
        };
        return map[status] || 'draft';
    }

    getCurrentDate() {
        return new Date().toLocaleDateString('en-SA', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    getHijriDate() {
        try {
            return new Date().toLocaleDateString('ar-SA-u-ca-islamic', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        } catch {
            return '';
        }
    }
}

registry.category("actions").add("saudi_erp_dashboard.main_dashboard", SaudiDashboard);
