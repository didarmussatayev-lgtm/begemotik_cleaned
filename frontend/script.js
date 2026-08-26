// BACKEND_URL is defined in config.js — change it to your deployed FastAPI URL

// ── i18n ──────────────────────────────────────────────────────────────────
const I18N = {
  ru: {
    start: 'НАЧАТЬ',
    formTitle: 'Заполнение согласия',
    sectionPatient: 'Основная информация о пациенте',
    labelIIN: 'ИИН',
    labelSurname: 'Фамилия',
    labelName: 'Имя',
    labelLastName: 'Отчество (если имеется)',
    labelGender: 'Пол',
    genderPlaceholder: 'Выберите пол',
    genderMale: 'мужской',
    genderFemale: 'женский',
    labelBirthdate: 'Дата рождения',
    labelPhone: 'Телефон',
    labelHasKinship: 'Законный представитель пациента',
    labelSurnameKinship: 'Фамилия представителя',
    labelNameKinship: 'Имя представителя',
    labelLastNameKinship: 'Отчество представителя (если имеется)',
    labelDegreeKinship: 'Степень родства',
    degreeKinshipPlaceholder: 'Выберите степень родства',
    degreeKinshipChild: 'ребенок',
    degreeKinshipRep: 'лицо, чьим законным представителем я являюсь',
    labelHasAllergy: 'Есть аллергия',
    labelAllergyText: 'Укажите аллергию',
    labelProcedure: 'Проводимые процедуры',
    labelSignature: 'Подпись',
    hintSignature: 'Нарисуйте подпись в поле ниже',
    btnClearSig: 'Очистить',
    labelConsentFacsimile: 'Даю согласие на использование факсимиле',
    labelConsentPersonal: 'Даю согласие на сбор персональных данных',
    btnBack: 'НАЗАД',
    btnNext: 'ДАЛЕЕ',
    btnSign: 'ПОДПИСАТЬ',
    loadingTitle: 'Формируем соглашение…',
    loadingSubtitle: 'Обычно это занимает меньше минуты',
    // validation errors
    errIINRequired: 'Введите ИИН',
    errIINFormat: 'ИИН должен содержать 12 цифр',
    errSurnameRequired: 'Введите фамилию',
    errCyrillic: 'Должно содержать только кириллические буквы',
    errNameRequired: 'Введите имя',
    errGenderRequired: 'Выберите пол',
    errBirthdateRequired: 'Введите дату рождения',
    errBirthdateFormat: 'Формат: ДД.ММ.ГГГГ',
    errBirthdateFuture: 'Дата не может быть в будущем',
    errPhoneRequired: 'Введите телефон',
    errPhoneFormat: 'Формат: +7 (7XX) XXX-XX-XX',
    errKinshipSurnameRequired: 'Введите фамилию представителя',
    errKinshipNameRequired: 'Введите имя представителя',
    errDegreeRequired: 'Выберите степень родства',
    errAllergyRequired: 'Укажите аллергию',
    errProcedureRequired: 'Укажите процедуру',
    errSignatureRequired: 'Нарисуйте подпись',
  },
  kz: {
    start: 'БАСТАУ',
    formTitle: 'Келісімді толтыру',
    sectionPatient: 'Пациент туралы негізгі ақпарат',
    labelIIN: 'ЖСН',
    labelSurname: 'Тегі',
    labelName: 'Аты',
    labelLastName: 'Әкесінің аты (болса)',
    labelGender: 'Жынысы',
    genderPlaceholder: 'Жынысты таңдаңыз',
    genderMale: 'еркек',
    genderFemale: 'әйел',
    labelBirthdate: 'Туған күні',
    labelPhone: 'Телефон',
    labelHasKinship: 'Пациенттің заңды өкілі',
    labelSurnameKinship: 'Өкілдің тегі',
    labelNameKinship: 'Өкілдің аты',
    labelLastNameKinship: 'Өкілдің әкесінің аты (болса)',
    labelDegreeKinship: 'Туыстық дәрежесі',
    degreeKinshipPlaceholder: 'Туыстық дәрежесін таңдаңыз',
    degreeKinshipChild: 'бала',
    degreeKinshipRep: 'заңды өкілі болып табылатын тұлға',
    labelHasAllergy: 'Аллергия бар',
    labelAllergyText: 'Аллергияны көрсетіңіз',
    labelProcedure: 'Жүргізілетін процедуралар',
    labelSignature: 'Қол қою',
    hintSignature: 'Төмендегі өріске қол қойыңыз',
    btnClearSig: 'Тазалау',
    labelConsentFacsimile: 'Факсимиле пайдалануға келісемін',
    labelConsentPersonal: 'Жеке деректерді жинауға келісемін',
    btnBack: 'АРТҚА',
    btnNext: 'КЕЛЕСІ',
    btnSign: 'ҚОЛ ҚОЮ',
    loadingTitle: 'Келісімді дайындаудамыз…',
    loadingSubtitle: 'Бұл бір минуттан аз уақытты алады',
    errIINRequired: 'ЖСН енгізіңіз',
    errIINFormat: 'ЖСН 12 саннан тұруы тиіс',
    errSurnameRequired: 'Тегіңізді енгізіңіз',
    errCyrillic: 'Тек кириллица әріптерін қолданыңыз',
    errNameRequired: 'Атыңызды енгізіңіз',
    errGenderRequired: 'Жынысты таңдаңыз',
    errBirthdateRequired: 'Туған күнін енгізіңіз',
    errBirthdateFormat: 'Формат: КК.АА.ЖЖЖЖ',
    errBirthdateFuture: 'Күн болашақта болмауы тиіс',
    errPhoneRequired: 'Телефонды енгізіңіз',
    errPhoneFormat: 'Формат: +7 (7XX) XXX-XX-XX',
    errKinshipSurnameRequired: 'Өкілдің тегін енгізіңіз',
    errKinshipNameRequired: 'Өкілдің атын енгізіңіз',
    errDegreeRequired: 'Туыстық дәрежесін таңдаңыз',
    errAllergyRequired: 'Аллергияны көрсетіңіз',
    errProcedureRequired: 'Процедураны көрсетіңіз',
    errSignatureRequired: 'Қол қойыңыз',
  },
};

let currentLang = 'ru';

function t(key) {
  return (I18N[currentLang] && I18N[currentLang][key]) || I18N.ru[key] || key;
}

function applyI18n() {
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    const key = el.getAttribute('data-i18n');
    const val = t(key);
    if (el.tagName === 'OPTION') {
      el.textContent = val;
    } else if (el.tagName === 'BUTTON' || el.tagName === 'LABEL' || el.tagName === 'H2' || el.tagName === 'H3' || el.tagName === 'P') {
      // For labels that contain child elements, only update the text node
      const firstTextNode = [...el.childNodes].find((n) => n.nodeType === Node.TEXT_NODE);
      if (firstTextNode) {
        firstTextNode.textContent = val;
      } else {
        el.textContent = val;
      }
    } else {
      el.textContent = val;
    }
  });
  // Update gender option values to match current language mapping (keep internal values)
  // Language switch only changes display text, internal values stay in Russian for backend
}

// ── State ─────────────────────────────────────────────────────────────────
let currentStep = 1;
let canvas;
let ctx;
let isDrawing = false;
let hasSignature = false;

// ── Init ──────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initLangSwitcher();
  initModal();
  initCanvas();
  initListeners();
  showStep(1);
  applyI18n();
});

function initLangSwitcher() {
  document.getElementById('langRU')?.addEventListener('click', () => setLang('ru'));
  document.getElementById('langKZ')?.addEventListener('click', () => setLang('kz'));
}

function setLang(lang) {
  currentLang = lang;
  document.getElementById('langRU').classList.toggle('active', lang === 'ru');
  document.getElementById('langKZ').classList.toggle('active', lang === 'kz');
  applyI18n();
}

function initModal() {
  const startBtn = document.getElementById('startBtn');
  const closeBtn = document.getElementById('closeModal');
  const modal = document.getElementById('formModal');

  startBtn?.addEventListener('click', () => {
    resetWizardState();
    modal.style.display = 'flex';
    showStep(1);
    resizeCanvas();
  });

  closeBtn?.addEventListener('click', () => {
    modal.style.display = 'none';
  });
}

function initListeners() {
  document.getElementById('nextStep1')?.addEventListener('click', () => {
    if (!validateStep1()) return;
    showStep(2);
  });

  document.getElementById('nextStep2')?.addEventListener('click', () => {
    if (!validateStep2()) return;
    showStep(3);
  });

  document.getElementById('backStep2')?.addEventListener('click', () => showStep(1));
  document.getElementById('backStep3')?.addEventListener('click', () => showStep(2));

  document.getElementById('hasKinship')?.addEventListener('change', toggleKinshipFields);
  document.getElementById('hasAllergy')?.addEventListener('change', toggleAllergyField);

  document.getElementById('iin')?.addEventListener('input', handleIINInput);
  document.getElementById('birthdate')?.addEventListener('input', handleBirthdateInput);

  document.querySelectorAll('.phone-input').forEach((input) => {
    input.addEventListener('input', handlePhoneInput);
  });

  document.getElementById('consentForm')?.addEventListener('submit', handleSubmit);
}

function resetWizardState() {
  currentStep = 1;
  document.getElementById('consentForm')?.reset();
  clearSignature();
  document.getElementById('errorMessage').style.display = 'none';
  document.getElementById('errorMessage').textContent = '';
  toggleKinshipFields();
  toggleAllergyField();
}

function showStep(step) {
  currentStep = step;
  document.getElementById('step1').style.display = step === 1 ? 'block' : 'none';
  document.getElementById('step2').style.display = step === 2 ? 'block' : 'none';
  document.getElementById('step3').style.display = step === 3 ? 'block' : 'none';

  if (step === 3) resizeCanvas();
}

function toggleKinshipFields() {
  const checked = document.getElementById('hasKinship')?.checked ?? false;
  document.getElementById('kinshipFields').style.display = checked ? 'block' : 'none';
}

function toggleAllergyField() {
  const checked = document.getElementById('hasAllergy')?.checked ?? false;
  document.getElementById('allergyField').style.display = checked ? 'block' : 'none';
}

// ── Validation helpers ────────────────────────────────────────────────────
function setFieldError(inputId, errorId, message) {
  const input = document.getElementById(inputId);
  const error = document.getElementById(errorId);
  if (input) input.classList.toggle('error', !!message);
  if (error) error.textContent = message;
}

function validateCyrillic(value) {
  return /^[А-Яа-яЁёӘәҒғҚқҢңӨөҰұҮүҺһІі\s\-]+$/.test(value);
}

function validateStep1() {
  let ok = true;

  const iin = document.getElementById('iin')?.value.trim() ?? '';
  if (!iin) { setFieldError('iin', 'iin-error', t('errIINRequired')); ok = false; }
  else if (!/^\d{12}$/.test(iin)) { setFieldError('iin', 'iin-error', t('errIINFormat')); ok = false; }
  else setFieldError('iin', 'iin-error', '');

  const surname = document.getElementById('surname')?.value.trim() ?? '';
  if (!surname) { setFieldError('surname', 'surname-error', t('errSurnameRequired')); ok = false; }
  else if (!validateCyrillic(surname)) { setFieldError('surname', 'surname-error', t('errCyrillic')); ok = false; }
  else setFieldError('surname', 'surname-error', '');

  const name = document.getElementById('name')?.value.trim() ?? '';
  if (!name) { setFieldError('name', 'name-error', t('errNameRequired')); ok = false; }
  else if (!validateCyrillic(name)) { setFieldError('name', 'name-error', t('errCyrillic')); ok = false; }
  else setFieldError('name', 'name-error', '');

  const lastName = document.getElementById('last_name')?.value.trim() ?? '';
  if (lastName && !validateCyrillic(lastName)) { setFieldError('last_name', 'last_name-error', t('errCyrillic')); ok = false; }
  else setFieldError('last_name', 'last_name-error', '');

  const gender = document.getElementById('gender')?.value ?? '';
  if (!gender) { setFieldError('gender', 'gender-error', t('errGenderRequired')); ok = false; }
  else setFieldError('gender', 'gender-error', '');

  const birthdate = document.getElementById('birthdate')?.value.trim() ?? '';
  if (!birthdate) { setFieldError('birthdate', 'birthdate-error', t('errBirthdateRequired')); ok = false; }
  else if (!isValidBirthdate(birthdate)) { setFieldError('birthdate', 'birthdate-error', t('errBirthdateFormat')); ok = false; }
  else if (isBirthdateFuture(birthdate)) { setFieldError('birthdate', 'birthdate-error', t('errBirthdateFuture')); ok = false; }
  else setFieldError('birthdate', 'birthdate-error', '');

  if (!validatePhoneById('phone', 'phone-error')) ok = false;

  if (document.getElementById('hasKinship')?.checked) {
    const sk = document.getElementById('surname_kinship')?.value.trim() ?? '';
    if (!sk) { setFieldError('surname_kinship', 'surname_kinship-error', t('errKinshipSurnameRequired')); ok = false; }
    else if (!validateCyrillic(sk)) { setFieldError('surname_kinship', 'surname_kinship-error', t('errCyrillic')); ok = false; }
    else setFieldError('surname_kinship', 'surname_kinship-error', '');

    const nk = document.getElementById('name_kinship')?.value.trim() ?? '';
    if (!nk) { setFieldError('name_kinship', 'name_kinship-error', t('errKinshipNameRequired')); ok = false; }
    else if (!validateCyrillic(nk)) { setFieldError('name_kinship', 'name_kinship-error', t('errCyrillic')); ok = false; }
    else setFieldError('name_kinship', 'name_kinship-error', '');

    const lnk = document.getElementById('last_name_kinship')?.value.trim() ?? '';
    if (lnk && !validateCyrillic(lnk)) { setFieldError('last_name_kinship', 'last_name_kinship-error', t('errCyrillic')); ok = false; }
    else setFieldError('last_name_kinship', 'last_name_kinship-error', '');

    const deg = document.getElementById('degree_of_kinship')?.value ?? '';
    if (!deg) { setFieldError('degree_of_kinship', 'degree_of_kinship-error', t('errDegreeRequired')); ok = false; }
    else setFieldError('degree_of_kinship', 'degree_of_kinship-error', '');
  }

  return ok;
}

function validateStep2() {
  let ok = true;

  if (document.getElementById('hasAllergy')?.checked) {
    const allergyText = document.getElementById('allergyText')?.value.trim() ?? '';
    if (!allergyText) { setFieldError('allergyText', 'allergyText-error', t('errAllergyRequired')); ok = false; }
    else setFieldError('allergyText', 'allergyText-error', '');
  } else {
    setFieldError('allergyText', 'allergyText-error', '');
  }

  const procedure = document.getElementById('procedure')?.value.trim() ?? '';
  if (!procedure) { setFieldError('procedure', 'procedure-error', t('errProcedureRequired')); ok = false; }
  else setFieldError('procedure', 'procedure-error', '');

  return ok;
}

function validateStep3() {
  let ok = true;
  if (!hasSignature) {
    document.getElementById('signature-error').textContent = t('errSignatureRequired');
    ok = false;
  } else {
    document.getElementById('signature-error').textContent = '';
  }
  return ok;
}

// ── Input handlers ────────────────────────────────────────────────────────
function validatePhoneById(inputId, errorId, required = true) {
  const value = document.getElementById(inputId)?.value.trim() ?? '';
  if (!value) {
    setFieldError(inputId, errorId, required ? t('errPhoneRequired') : '');
    return !required;
  }
  const digits = value.replace(/\D/g, '');
  const ok = /^77\d{9}$/.test(digits);
  setFieldError(inputId, errorId, ok ? '' : t('errPhoneFormat'));
  return ok;
}

function handlePhoneInput(e) {
  const input = e.target;
  let digits = input.value.replace(/\D/g, '');
  if (digits.startsWith('8')) digits = `7${digits.slice(1)}`;
  if (!digits.startsWith('7')) digits = `7${digits}`;
  digits = digits.slice(0, 11);
  let formatted = '+7';
  if (digits.length > 1) formatted += ` (${digits.slice(1, Math.min(4, digits.length))}`;
  if (digits.length >= 4) formatted += `) ${digits.slice(4, Math.min(7, digits.length))}`;
  if (digits.length >= 7) formatted += `-${digits.slice(7, Math.min(9, digits.length))}`;
  if (digits.length >= 9) formatted += `-${digits.slice(9, 11)}`;
  input.value = formatted;
}

function handleIINInput(e) {
  e.target.value = e.target.value.replace(/\D/g, '').slice(0, 12);
}

function handleBirthdateInput(e) {
  let v = e.target.value.replace(/\D/g, '').slice(0, 8);
  if (v.length > 4) v = `${v.slice(0, 2)}.${v.slice(2, 4)}.${v.slice(4)}`;
  else if (v.length > 2) v = `${v.slice(0, 2)}.${v.slice(2)}`;
  e.target.value = v;
}

function isValidBirthdate(value) {
  return /^\d{2}\.\d{2}\.\d{4}$/.test(value);
}

function isBirthdateFuture(value) {
  const [dd, mm, yyyy] = value.split('.');
  const d = new Date(`${yyyy}-${mm}-${dd}`);
  return !isNaN(d.getTime()) && d > new Date();
}

// ── Canvas / Signature ────────────────────────────────────────────────────
function initCanvas() {
  canvas = document.getElementById('signatureCanvas');
  if (!canvas) return;
  ctx = canvas.getContext('2d');
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);

  canvas.addEventListener('mousedown', startDraw);
  canvas.addEventListener('mousemove', continueDraw);
  canvas.addEventListener('mouseup', endDraw);
  canvas.addEventListener('mouseleave', endDraw);
  canvas.addEventListener('touchstart', handleTouchStart, { passive: false });
  canvas.addEventListener('touchmove', handleTouchMove, { passive: false });
  canvas.addEventListener('touchend', endDraw);

  document.getElementById('clearSignature')?.addEventListener('click', clearSignature);
}

function setCtxStyle() {
  ctx.strokeStyle = '#1E4FA3';
  ctx.lineWidth = 2;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
}

function resizeCanvas() {
  if (!canvas || !ctx) return;
  const rect = canvas.getBoundingClientRect();
  const snapshot = hasSignature ? ctx.getImageData(0, 0, canvas.width, canvas.height) : null;
  canvas.width = rect.width;
  canvas.height = rect.height;
  setCtxStyle();
  if (snapshot) ctx.putImageData(snapshot, 0, 0);
}

function startDraw(e) {
  isDrawing = true;
  const { x, y } = getPos(e);
  ctx.beginPath();
  ctx.moveTo(x, y);
}

function continueDraw(e) {
  if (!isDrawing) return;
  const { x, y } = getPos(e);
  ctx.lineTo(x, y);
  ctx.stroke();
  if (!hasSignature) {
    hasSignature = true;
    canvas.classList.add('has-signature');
  }
}

function endDraw() { isDrawing = false; }

function handleTouchStart(e) {
  e.preventDefault();
  const t = e.touches[0];
  startDraw({ clientX: t.clientX, clientY: t.clientY });
}

function handleTouchMove(e) {
  e.preventDefault();
  const t = e.touches[0];
  continueDraw({ clientX: t.clientX, clientY: t.clientY });
}

function getPos(e) {
  const rect = canvas.getBoundingClientRect();
  return { x: e.clientX - rect.left, y: e.clientY - rect.top };
}

function clearSignature() {
  if (!ctx || !canvas) return;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  hasSignature = false;
  canvas.classList.remove('has-signature');
  document.getElementById('signature-error').textContent = '';
}

function getSignatureBase64() {
  return canvas.toDataURL('image/png');
}

// ── Submit ────────────────────────────────────────────────────────────────
async function handleSubmit(e) {
  e.preventDefault();
  if (!validateStep3()) return;

  const submitBtn = document.getElementById('finishBtn');
  const errorBox = document.getElementById('errorMessage');
  errorBox.style.display = 'none';
  submitBtn.disabled = true;
  showLoadingModal();

  const hasKinship = document.getElementById('hasKinship')?.checked ?? false;
  const hasAllergy = document.getElementById('hasAllergy')?.checked ?? false;
  const allergyText = document.getElementById('allergyText')?.value.trim() ?? '';

  const payload = {
    iin: document.getElementById('iin').value.trim(),
    surname: document.getElementById('surname').value.trim(),
    name: document.getElementById('name').value.trim(),
    last_name: document.getElementById('last_name').value.trim(),
    gender: document.getElementById('gender').value,
    birthdate: document.getElementById('birthdate').value.trim(),
    phone: document.getElementById('phone').value.trim(),
    has_kinship: hasKinship,
    surname_kinship: hasKinship ? document.getElementById('surname_kinship').value.trim() : '',
    name_kinship: hasKinship ? document.getElementById('name_kinship').value.trim() : '',
    last_name_kinship: hasKinship ? document.getElementById('last_name_kinship').value.trim() : '',
    degree_of_kinship: hasKinship ? document.getElementById('degree_of_kinship').value : '',
    has_allergy: hasAllergy,
    allergy_text: hasAllergy ? allergyText : '',
    procedure: document.getElementById('procedure').value.trim(),
    signature_base64: getSignatureBase64(),
    consent_facsimile: document.getElementById('consentFacsimile')?.checked ?? false,
    consent_personal_data: document.getElementById('consentPersonal')?.checked ?? false,
  };

  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/agreements`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      let detail = `Ошибка сервера (${response.status})`;
      try {
        const data = await response.json();
        if (data.detail) detail = data.detail;
      } catch (_) {}
      throw new Error(detail);
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const disposition = response.headers.get('Content-Disposition') ?? '';
    const match = disposition.match(/filename[^;=\n]*=(['"]?)([^'";\n]+)\1/);
    a.download = match ? match[2] : 'med_centr_begemotik.pdf';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);

    document.getElementById('formModal').style.display = 'none';
  } catch (err) {
    console.error(err);
    errorBox.textContent = err.message || 'Произошла неизвестная ошибка. Попробуйте ещё раз.';
    errorBox.style.display = 'block';
    submitBtn.disabled = false;
  } finally {
    hideLoadingModal();
  }
}

function showLoadingModal() {
  document.getElementById('loadingModal').style.display = 'flex';
}

function hideLoadingModal() {
  document.getElementById('loadingModal').style.display = 'none';
}

