const express = require('express');
const router = express.Router();
const { uploadSiteImage } = require('../config/upload');
const { authenticateAdmin } = require('../middleware/auth');
const { uploadFile } = require('../services/storageService');
const {
  getPublic,
  updateSettings,
  updateLogo,
  deleteLogo,
} = require('../controllers/siteController');

const bearerToken = (req) => (req.headers.authorization || '').split(' ')[1] || null;

async function storeUpload(req, folder) {
  if (!req.file) return null;
  const stored = await uploadFile({
    buffer: req.file.buffer,
    originalname: req.file.originalname,
    mimetype: req.file.mimetype,
    folder,
    token: bearerToken(req),
  });
  return stored.url;
}

// Logos are limited to 10MB; multer errors must answer with JSON, not HTML.
function uploadLogo(req, res, next) {
  uploadSiteImage.single('image')(req, res, (error) => {
    if (!error) return next();
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({ success: false, message: 'حجم تصویر نباید بیشتر از ۱۰ مگابایت باشد' });
    }
    return res.status(400).json({ success: false, message: error.message || 'خطا در آپلود تصویر' });
  });
}

// Admin routes are declared before the public one.
router.put('/admin/settings', authenticateAdmin, updateSettings);

router.post('/admin/logo', authenticateAdmin, uploadLogo, async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ success: false, message: 'تصویری ارسال نشده است' });
    }
    const url = await storeUpload(req, 'site');
    if (!url) {
      return res.status(500).json({ success: false, message: 'ذخیره لوگو انجام نشد' });
    }
    req.body.logo_url = url;
    return updateLogo(req, res);
  } catch (error) {
    console.error('Upload site logo error:', error);
    res.status(500).json({ success: false, message: error.message || 'خطا در آپلود لوگو' });
  }
});

router.delete('/admin/logo', authenticateAdmin, deleteLogo);

router.get('/', getPublic);

module.exports = router;
