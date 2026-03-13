import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import healthRoutes from './routes/health.routes.js';
import patientsRoutes from './routes/patients.routes.js';
import predictionsRoutes from './routes/predictions.routes.js';
import historyRoutes from './routes/history.routes.js';
import reportsRoutes from './routes/reports.routes.js';
import assistantRoutes from './routes/assistant.routes.js';
import { errorHandler, notFoundHandler } from './middleware/error.middleware.js';

const app = express();

app.use(cors());
app.use(helmet());
app.use(morgan('dev'));
app.use(express.json({ limit: '1mb' }));

app.get('/', (_req, res) => {
  res.json({ service: 'Health AI Studio API', status: 'running' });
});

app.use('/api/health', healthRoutes);
app.use('/api/patients', patientsRoutes);
app.use('/api/predictions', predictionsRoutes);
app.use('/api/history', historyRoutes);
app.use('/api/reports', reportsRoutes);
app.use('/api/assistant', assistantRoutes);

app.use(notFoundHandler);
app.use(errorHandler);

export default app;
