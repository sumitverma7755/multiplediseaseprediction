import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const dataDirectory = path.resolve(__dirname, '../../data');

function resolveFile(fileName) {
  return path.join(dataDirectory, fileName);
}

export async function readCollection(fileName) {
  const filePath = resolveFile(fileName);
  try {
    const raw = await fs.readFile(filePath, 'utf8');
    return JSON.parse(raw || '[]');
  } catch (error) {
    if (error.code === 'ENOENT') {
      await fs.mkdir(dataDirectory, { recursive: true });
      await fs.writeFile(filePath, '[]');
      return [];
    }
    throw error;
  }
}

export async function writeCollection(fileName, items) {
  const filePath = resolveFile(fileName);
  await fs.mkdir(dataDirectory, { recursive: true });
  await fs.writeFile(filePath, JSON.stringify(items, null, 2));
}
