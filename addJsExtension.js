import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const directoryPath = path.join(__dirname, 'dist')

function addJsExtension(filePath) {
  let content = fs.readFileSync(filePath, 'utf8')
  content = content.replace(
    /(import\s.*?from\s+['"])(\.\/.*?)(['"])/g,
    '$1$2.js$3'
  )
  fs.writeFileSync(filePath, content, 'utf8')
}

function processDirectory(directory) {
  fs.readdirSync(directory).forEach(file => {
    const fullPath = path.join(directory, file)
    if (fs.lstatSync(fullPath).isDirectory()) {
      processDirectory(fullPath)
    } else if (file.endsWith('.js')) {
      addJsExtension(fullPath)
    }
  })
}

processDirectory(directoryPath)
