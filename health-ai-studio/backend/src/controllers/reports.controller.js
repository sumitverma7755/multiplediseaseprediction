import { getPredictionById, getPredictions } from '../services/predictionStore.service.js';
import { historyCsvBuffer, historyPdfBuffer, predictionReportPdf } from '../services/report.service.js';

export async function predictionReport(req, res, next) {
  try {
    const prediction = await getPredictionById(req.params.predictionId);
    if (!prediction) {
      const err = new Error('Prediction not found');
      err.statusCode = 404;
      throw err;
    }

    const pdfBuffer = await predictionReportPdf(prediction);
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename=ai-health-report-${prediction.id}.pdf`);
    res.send(pdfBuffer);
  } catch (error) {
    next(error);
  }
}

export async function historyExport(req, res, next) {
  try {
    const format = (req.query.format || 'csv').toLowerCase();
    const items = await getPredictions({
      diseaseType: req.query.diseaseType || '',
      patientId: req.query.patientId || '',
      dateFrom: req.query.dateFrom || '',
      dateTo: req.query.dateTo || ''
    });

    if (format === 'pdf') {
      const pdfBuffer = await historyPdfBuffer(items);
      res.setHeader('Content-Type', 'application/pdf');
      res.setHeader('Content-Disposition', 'attachment; filename=history-export.pdf');
      return res.send(pdfBuffer);
    }

    const csvBuffer = historyCsvBuffer(items);
    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', 'attachment; filename=history-export.csv');
    return res.send(csvBuffer);
  } catch (error) {
    next(error);
  }
}
