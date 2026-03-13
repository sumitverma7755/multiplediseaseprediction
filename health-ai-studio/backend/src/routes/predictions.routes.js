import { Router } from 'express';
import { createPrediction, weeklyPredictionTrend } from '../controllers/predictions.controller.js';

const router = Router();

router.post('/', createPrediction);
router.get('/trends/weekly', weeklyPredictionTrend);

export default router;
