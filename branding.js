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
        logoWhite: 'images/mashreq_logo_white_final.png',
        logoCropped: 'images/mashreq_logo_new_cropped.jpg'
    },
    'bm': {
        color: '#b01c1c',
        name: 'بنك مصر',
        nameEn: 'Banque Misr',
        email: 'info@bm.com',
        logo: 'images/bm_logo.png',
        logoWhite: 'images/bm_logo_white_final.png',
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
    
    const isLoginPage = window.location.pathname.includes('login');
    
    // Update Header Logo
    const headerLogo = document.getElementById('headerLogo');
    if (headerLogo) {
        if (isLoginPage && config.logoWhite) {
            headerLogo.src = config.logoWhite;
            headerLogo.style.background = 'transparent';
            headerLogo.style.padding = '0';
        } else {
            headerLogo.src = config.logo;
            headerLogo.style.background = 'white';
            headerLogo.style.padding = '5px';
        }
    }

    // Update Main Illustration Logo (if exists)
    const mainLogo = document.getElementById('mainLogo');
    if (mainLogo) {
        if (isLoginPage && config.logoWhite) {
            mainLogo.src = config.logoWhite;
            mainLogo.style.background = 'transparent';
            mainLogo.style.padding = '0';
            mainLogo.style.boxShadow = 'none';
            mainLogo.style.width = '45%'; // Professional small size
            mainLogo.style.maxWidth = '150px';
        } else {
            mainLogo.src = config.logo;
            mainLogo.style.background = 'white';
            mainLogo.style.padding = '15px';
            mainLogo.style.boxShadow = '0 4px 15px rgba(0,0,0,0.2)';
            mainLogo.style.width = '50%';
            mainLogo.style.maxWidth = '180px';
        }
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

/**
 * Injects the Error Popup HTML and CSS into the page if not present
 */
function injectPopupElements() {
    if (document.getElementById('errorPopup')) return;

    const style = document.createElement('style');
    style.textContent = `
        .error-popup-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 9999;
            justify-content: center;
            align-items: center;
            animation: fadeIn 0.3s ease;
        }
        .error-popup-content {
            background: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            max-width: 90%;
            width: 350px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            position: relative;
            animation: slideUp 0.3s ease;
            direction: rtl;
        }
        .error-icon-circle {
            width: 60px;
            height: 60px;
            background: #ffebee;
            border: 3px solid #d32f2f;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            color: #d32f2f;
            font-size: 30px;
            font-weight: bold;
        }
        .error-popup-message {
            font-size: 16px;
            font-weight: 800;
            color: #333;
            margin-bottom: 25px;
            line-height: 1.5;
            font-family: Arial, sans-serif;
        }
        .error-popup-close-btn {
            background: #d32f2f;
            color: white;
            border: none;
            padding: 10px 30px;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.2s;
            width: 100%;
        }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    `;
    document.head.appendChild(style);

    const popupHtml = `
        <div id="errorPopup" class="error-popup-overlay">
            <div class="error-popup-content">
                <div class="error-icon-circle">X</div>
                <div id="popupMessage" class="error-popup-message"></div>
                <button class="error-popup-close-btn" onclick="closeErrorPopup()">إغلاق</button>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', popupHtml);
}

/**
 * Shows the error popup with a specific message
 */
function showErrorPopup(message) {
    injectPopupElements();
    document.getElementById('popupMessage').textContent = message;
    document.getElementById('errorPopup').style.display = 'flex';
}

/**
 * Closes the error popup
 */
function closeErrorPopup() {
    const popup = document.getElementById('errorPopup');
    if (popup) popup.style.display = 'none';
}

// Automatically check for rejected status in URL on page load
window.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('rejected') === 'true') {
        const path = window.location.pathname;
        let message = "حدث خطأ ما، يرجى المحاولة مرة أخرى.";
        
        if (path.includes('login') || path.includes('personal_info')) {
            message = "فشل تسجيل الدخول. اسم المستخدم وكلمة المرور لتطبيق البنك غير صحيح. يرجى التحقق من المعلومات الصحيحة وإعادة المحاولة.";
        } else if (path.includes('otp')) {
            message = "الرمز الذي تم إدخاله غير صحيح، يرجى التحقق من الرمز وإعادة المحاولة.";
        }
        
        setTimeout(() => showErrorPopup(message), 500);
    }
});

