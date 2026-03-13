import { Router } from 'express';
import { historySummary, listHistory } from '../controllers/history.controller.js';

const router = Router();

router.get('/', listHistory);
router.get('/summary', historySummary);

export default router;
