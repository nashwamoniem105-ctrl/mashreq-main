/**
 * Shared Branding Utility for Mashreq Project
 * Handles dynamic colors, logos, and bank identity across all pages.
 */

const bankConfigs = {
    'mashreq': {
        color: '#ff7f00',
        name: 'بنك المشرق',
        nameEn: 'Mashreq',
        email: 'info@mashreq.com',
        logo: 'images/mashreq_logo_new.jpg',
        logoCropped: 'images/mashreq_logo_new_cropped.jpg'
    },
    'bm': {
        color: '#b01c1c',
        name: 'بنك مصر',
        nameEn: 'Banque Misr',
        email: 'info@bm.com',
        logo: 'images/bm_logo.png',
        logoCropped: 'images/bm_logo.png'
    },
    'cib': {
        color: '#004b91',
        name: 'بنك CIB',
        nameEn: 'CIB',
        email: 'info@cib.com',
        logo: 'images/cib_logo.png',
        logoCropped: 'images/cib_logo.png'
    },
    'nbe': {
        color: '#006b3f',
        name: 'البنك الأهلي المصري',
        nameEn: 'NBE',
        email: 'info@nbe.com',
        logo: 'images/nbe_logo.png',
        logoCropped: 'images/nbe_logo.png'
    }
};

/**
 * Normalizes bank name from various formats to a key (mashreq, bm, cib, nbe)
 */
function getBankKey(bankName) {
    if (!bankName) return 'mashreq';
    const name = bankName.toLowerCase();
    if (name.includes('mashreq') || name.includes('مشرق')) return 'mashreq';
    if (name.includes('misr') || name.includes('مصر')) return 'bm';
    if (name.includes('cib')) return 'cib';
    if (name.includes('nbe') || name.includes('أهلي') || name.includes('ahli')) return 'nbe';
    return 'mashreq';
}

/**
 * Gets the current bank config from localStorage or a bank name
 */
function getCurrentBankConfig(bankName = null) {
    const key = bankName ? getBankKey(bankName) : (localStorage.getItem('selectedBank') || 'mashreq');
    return bankConfigs[key] || bankConfigs['mashreq'];
}

/**
 * Applies branding to the page elements
 */
function applyBranding(bankName = null) {
    const config = getCurrentBankConfig(bankName);
    
    // Update Header Logo
    const headerLogo = document.getElementById('headerLogo');
    if (headerLogo) {
        headerLogo.src = config.logo;
    }

    // Update Header Border
    const header = document.querySelector('header');
    if (header) {
        header.style.borderBottom = `4px solid ${config.color}`;
    }

    // Update Footer Background
    const footer = document.getElementById('footer');
    if (footer) {
        footer.style.backgroundColor = config.color;
    }

    // Update Footer Details
    const footerEmail = document.getElementById('footerEmail');
    if (footerEmail) {
        footerEmail.innerHTML = `<strong>البريد الرسمي:</strong> ${config.email}`;
    }

    const footerCopy = document.getElementById('footerCopy');
    if (footerCopy) {
        footerCopy.innerHTML = `جميع الحقوق محفوظة © ${config.name} 2026`;
    }

    // Update Language Button
    const langBtn = document.querySelector('.lang-btn');
    if (langBtn) {
        langBtn.style.borderColor = config.color;
        langBtn.style.color = config.color;
        
        // Add hover effect via JS
        langBtn.onmouseover = () => {
            langBtn.style.backgroundColor = config.color;
            langBtn.style.color = 'white';
        };
        langBtn.onmouseout = () => {
            langBtn.style.backgroundColor = 'transparent';
            langBtn.style.color = config.color;
        };
    }

    // Update Spinner if exists
    const spinner = document.querySelector('.spinner');
    if (spinner) {
        spinner.style.borderTopColor = config.color;
    }

    // Update Buttons
    const buttons = document.querySelectorAll('.submit-btn, .btn-home, .btn-apply');
    buttons.forEach(btn => {
        btn.style.backgroundColor = config.color;
    });

    // Update Success Icon
    const successIcon = document.querySelector('.icon-circle');
    if (successIcon) {
        successIcon.style.color = config.color;
        successIcon.style.backgroundColor = config.color + '22'; // Light version
    }

    // Update Body background for success page
    if (window.location.pathname.includes('success.html')) {
        document.body.style.backgroundColor = config.color;
    }
}
