import { Router } from 'express';
import { historyExport, predictionReport } from '../controllers/reports.controller.js';

const router = Router();

router.get('/prediction/:predictionId', predictionReport);
router.get('/history', historyExport);

export default router;
