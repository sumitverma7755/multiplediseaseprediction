import PDFDocument from 'pdfkit';
import { Parser } from 'json2csv';

function buildPdfBuffer(writeFn) {
  return new Promise((resolve, reject) => {
    const doc = new PDFDocument({ margin: 40 });
    const chunks = [];
    doc.on('data', (chunk) => chunks.push(chunk));
    doc.on('end', () => resolve(Buffer.concat(chunks)));
    doc.on('error', reject);

    writeFn(doc);
    doc.end();
  });
}

export function predictionReportPdf(prediction) {
  return buildPdfBuffer((doc) => {
    doc.fontSize(20).text('AI Health Report', { underline: true });
    doc.moveDown();

    doc.fontSize(12).text(`Patient: ${prediction.patientName}`);
    doc.text(`Disease Type: ${prediction.diseaseType}`);
    doc.text(`Generated At: ${new Date(prediction.createdAt).toLocaleString()}`);
    doc.moveDown();

    doc.fontSize(14).text('Prediction Result', { underline: true });
    doc.fontSize(12).text(`Risk Score: ${prediction.riskPercentage.toFixed(1)}%`);
    doc.text(`Risk Category: ${prediction.riskCategory}`);
    doc.text(`Confidence Score: ${prediction.confidenceScore.toFixed(1)}%`);
    doc.moveDown();

    doc.fontSize(14).text('Top Important Features', { underline: true });
    prediction.featureImportance.forEach((item, idx) => {
      doc.fontSize(12).text(`${idx + 1}. ${item.feature}: ${(item.importance * 100).toFixed(1)}%`);
    });
    doc.moveDown();

    doc.fontSize(14).text('AI Recommendations', { underline: true });
    prediction.recommendations.forEach((line, idx) => {
      doc.fontSize(12).text(`- ${line}`);
    });

    doc.moveDown();
    doc.fillColor('gray').fontSize(10).text('Medical Disclaimer: AI predictions are informational and not a substitute for professional medical diagnosis.');
  });
}

export function historyCsvBuffer(predictions) {
  const parser = new Parser({
    fields: ['createdAt', 'patientName', 'diseaseType', 'riskPercentage', 'riskCategory', 'confidenceScore']
  });
  return Buffer.from(parser.parse(predictions), 'utf8');
}

export function historyPdfBuffer(predictions) {
  return buildPdfBuffer((doc) => {
    doc.fontSize(18).text('Prediction History Report', { underline: true });
    doc.moveDown();

    predictions.forEach((item, idx) => {
      doc.fontSize(12).text(`${idx + 1}. ${new Date(item.createdAt).toLocaleString()} - ${item.patientName || 'N/A'}`);
      doc.text(`   ${item.diseaseType} | Risk ${item.riskPercentage.toFixed(1)}% | ${item.riskCategory} | Confidence ${item.confidenceScore.toFixed(1)}%`);
      doc.moveDown(0.6);
    });

    if (!predictions.length) {
      doc.text('No prediction records available for selected filters.');
    }
  });
}
