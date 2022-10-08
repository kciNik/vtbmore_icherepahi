const Router = require('express').Router;

const router = new Router();

router.post('/login');
router.post('/logout');
router.get('/refresh');
router.get('/user');

module.exports = router
