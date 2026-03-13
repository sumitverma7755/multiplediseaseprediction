import { Router } from 'express';
import { assistantChat } from '../controllers/assistant.controller.js';

const router = Router();

router.post('/chat', assistantChat);

export default router;
