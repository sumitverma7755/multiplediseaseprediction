import { getAssistantReply } from '../services/assistant.service.js';

export async function assistantChat(req, res, next) {
  try {
    const { question, context } = req.body;
    if (!question) {
      const err = new Error('question is required');
      err.statusCode = 400;
      throw err;
    }

    const reply = await getAssistantReply({ question, context });
    res.json(reply);
  } catch (error) {
    next(error);
  }
}
