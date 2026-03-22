/** @odoo-module **/
/**
 * Saudi ERP Base JS
 * - Hijri calendar helpers
 * - Arabic number formatting
 * - Saudi phone validation
 */

export function toHijri(gregorianDate) {
    try {
        return new Date(gregorianDate).toLocaleDateString('ar-SA-u-ca-islamic', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        });
    } catch (e) {
        return '';
    }
}

export function formatSAR(amount) {
    return new Intl.NumberFormat('en-SA', {
        style: 'currency',
        currency: 'SAR',
        minimumFractionDigits: 2,
    }).format(amount);
}

export function validateSaudiPhone(phone) {
    const cleaned = phone.replace(/[\s\-\(\)]/g, '');
    return /^(\+966|00966|0)(5\d{8})$/.test(cleaned);
}

export function validateSaudiIBAN(iban) {
    return /^SA\d{22}$/.test(iban.replace(/\s/g, ''));
}

export function validateVATNumber(vat) {
    return /^\d{15}$/.test(vat) && vat.startsWith('3');
}
