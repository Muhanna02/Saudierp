/**
 * Saudi ERP Portal JS
 * Registration form, plan selection, animations
 */

document.addEventListener('DOMContentLoaded', function() {

    // Plan radio button selection styling
    const planRadios = document.querySelectorAll('.plan-radio input[type="radio"]');
    planRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            document.querySelectorAll('.plan-radio').forEach(el => el.classList.remove('selected'));
            if (this.checked) {
                this.closest('.plan-radio').classList.add('selected');
            }
        });
        // Init selected state
        if (radio.checked) {
            radio.closest('.plan-radio').classList.add('selected');
        }
    });

    // VAT Number formatting (Saudi format: 15 digits)
    const vatInput = document.querySelector('input[name="vat_number"]');
    if (vatInput) {
        vatInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '').substring(0, 15);
            if (this.value.length === 15) {
                this.style.borderColor = '#1a7a4e';
            } else if (this.value.length > 0) {
                this.style.borderColor = '#f59e0b';
            }
        });
    }

    // Phone number formatting (Saudi: +966)
    const phoneInput = document.querySelector('input[name="admin_phone"]');
    if (phoneInput) {
        phoneInput.addEventListener('focus', function() {
            if (!this.value.startsWith('+966') && !this.value.startsWith('05')) {
                // Don't auto-fill, just hint
            }
        });
    }

    // Animate hero elements on load
    const heroContent = document.querySelector('.hero-content');
    if (heroContent) {
        heroContent.style.opacity = '0';
        heroContent.style.transform = 'translateY(20px)';
        setTimeout(() => {
            heroContent.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            heroContent.style.opacity = '1';
            heroContent.style.transform = 'translateY(0)';
        }, 100);
    }

    // Animate KPI cards staggered
    const previewKpis = document.querySelectorAll('.preview-kpi');
    previewKpis.forEach((kpi, i) => {
        kpi.style.opacity = '0';
        kpi.style.transform = 'translateY(10px)';
        setTimeout(() => {
            kpi.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            kpi.style.opacity = '1';
            kpi.style.transform = 'translateY(0)';
        }, 300 + i * 100);
    });

    // Animate chart bars
    const chartBars = document.querySelectorAll('.chart-bar');
    chartBars.forEach((bar, i) => {
        const targetHeight = bar.style.height;
        bar.style.height = '0%';
        setTimeout(() => {
            bar.style.transition = 'height 0.6s ease';
            bar.style.height = targetHeight;
        }, 600 + i * 80);
    });

    // Intersection Observer for scroll animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.feature-card, .pricing-card').forEach(el => {
        observer.observe(el);
    });

    // Registration form validation
    const form = document.querySelector('form[action="/register/submit"]');
    if (form) {
        form.addEventListener('submit', function(e) {
            const btn = form.querySelector('.btn-register-submit');
            if (btn) {
                btn.textContent = 'Creating your account... / جاري إنشاء الحساب...';
                btn.disabled = true;
            }
        });
    }
});
