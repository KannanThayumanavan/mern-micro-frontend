const fs = require('fs');
const path = require('path');
const glob = require('glob');

describe('No Enzyme imports in test suite', () => {
  const ENZYME_PACKAGES = [
    'enzyme',
    'enzyme-adapter-react-16',
    'enzyme-adapter-react-17',
    'enzyme-adapter-react-18',
    'enzyme-to-json',
    'enzyme-matchers',
    'jest-enzyme',
    'enzyme-adapter-utils',
    'enzyme-react-intl',
  ];

  const ENZYME_IMPORT_PATTERNS = ENZYME_PACKAGES.map(pkg => {
    const escapedPkg = pkg.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&');
    return new RegExp(
      `(import\\s+.*from\\s+['"]${escapedPkg}['"]|require\\s*\\(\\s*['"]${escapedPkg}['"]\\s*\\))`,
      'g'
    );
  });

  const SEARCH_DIRS = ['src', 'tests'];
  const FILE_EXTENSIONS = ['**/*.test.js', '**/*.test.jsx', '**/*.test.ts', '**/*.test.tsx', '**/*.spec.js', '**/*.spec.jsx', '**/*.spec.ts', '**/*.spec.tsx', '**/*.js', '**/*.jsx', '**/*.ts', '**/*.tsx'];

  function getFilesToScan() {
    const files = new Set();
    const projectRoot = path.resolve(__dirname, '..', '..');

    SEARCH_DIRS.forEach(dir => {
      const dirPath = path.join(projectRoot, dir);

      if (!fs.existsSync(dirPath)) {
        return;
      }

      FILE_EXTENSIONS.forEach(pattern => {
        const matches = glob.sync(pattern, {
          cwd: dirPath,
          absolute: true,
          nodir: true,
          ignore: ['**/node_modules/**'],
        });
        matches.forEach(f => files.add(f));
      });
    });

    return Array.from(files);
  }

  function scanFileForEnzymeImports(filePath) {
    let content;
    try {
      content = fs.readFileSync(filePath, 'utf8');
    } catch (err) {
      return { filePath, error: err.message, matches: [] };
    }

    const matches = [];

    ENZYME_PACKAGES.forEach((pkg, idx) => {
      const pattern = ENZYME_IMPORT_PATTERNS[idx];
      pattern.lastIndex = 0;
      let match;
      while ((match = pattern.exec(content)) !== null) {
        const lineNumber = content.substring(0, match.index).split('\n').length;
        matches.push({
          package: pkg,
          statement: match[0].trim(),
          line: lineNumber,
        });
      }
    });

    return { filePath, error: null, matches };
  }

  describe('Directory existence checks', () => {
    SEARCH_DIRS.forEach(dir => {
      it(`should be able to access the ${dir}/ directory if it exists`, () => {
        const projectRoot = path.resolve(__dirname, '..', '..');
        const dirPath = path.join(projectRoot, dir);

        if (fs.existsSync(dirPath)) {
          const stat = fs.statSync(dirPath);
          expect(stat.isDirectory()).toBe(true);
        } else {
          expect(true).toBe(true);
        }
      });
    });
  });

  describe('Enzyme package import detection', () => {
    it('should detect enzyme import statements correctly using regex', () => {
      const testCases = [
        { code: "import Enzyme from 'enzyme';", pkg: 'enzyme', shouldMatch: true },
        { code: 'import Enzyme from "enzyme";', pkg: 'enzyme', shouldMatch: true },
        { code: "import { shallow, mount } from 'enzyme';", pkg: 'enzyme', shouldMatch: true },
        { code: "const Enzyme = require('enzyme');", pkg: 'enzyme', shouldMatch: true },
        { code: 'const Enzyme = require("enzyme");', pkg: 'enzyme', shouldMatch: true },
        { code: "import Adapter from 'enzyme-adapter-react-16';", pkg: 'enzyme-adapter-react-16', shouldMatch: true },
        { code: "const Adapter = require('enzyme-adapter-react-16');", pkg: 'enzyme-adapter-react-16', shouldMatch: true },
        { code: "import { render } from '@testing-library/react';", pkg: 'enzyme', shouldMatch: false },
        { code: "// import Enzyme from 'enzyme';", pkg: 'enzyme', shouldMatch: false },
        { code: "import enzymeHelper from './enzyme-helper';", pkg: 'enzyme', shouldMatch: false },
      ];

      testCases.forEach(({ code, pkg, shouldMatch }) => {
        const pkgIndex = ENZYME_PACKAGES.indexOf(pkg);
        if (pkgIndex === -1) return;

        const pattern = ENZYME_IMPORT_PATTERNS[pkgIndex];
        pattern.lastIndex = 0;
        const result = pattern.test(code);
        pattern.lastIndex = 0;

        expect(result).toBe(shouldMatch);
      });
    });

    ENZYME_PACKAGES.forEach(pkg => {
      it(`should have a valid regex pattern for package: ${pkg}`, () => {
        const pkgIndex = ENZYME_PACKAGES.indexOf(pkg);
        expect(pkgIndex).toBeGreaterThanOrEqual(0);

        const pattern = ENZYME_IMPORT_PATTERNS[pkgIndex];
        expect(pattern).toBeInstanceOf(RegExp);

        const importStatement = `import something from '${pkg}';`;
        pattern.lastIndex = 0;
        expect(pattern.test(importStatement)).toBe(true);
        pattern.lastIndex = 0;

        const requireStatement = `const something = require('${pkg}');`;
        pattern.lastIndex = 0;
        expect(pattern.test(requireStatement)).toBe(true);
        pattern.lastIndex = 0;
      });
    });
  });

  describe('File scanning - no Enzyme imports allowed', () => {
    let filesToScan;
    let scanResults;

    beforeAll(() => {
      filesToScan = getFilesToScan();
      scanResults = filesToScan.map(filePath => scanFileForEnzymeImports(filePath));
    });

    it('should be able to scan files without filesystem errors', () => {
      const filesWithErrors = scanResults.filter(r => r.error !== null);
      if (filesWithErrors.length > 0) {
        const errorMessages = filesWithErrors
          .map(r => `  ${r.filePath}: ${r.error}`)
          .join('\n');
        console.warn(`Warning: Could not read some files:\n${errorMessages}`);
      }
      expect(filesWithErrors.length).toBe(0);
    });

    it('should find no enzyme imports in any scanned file', () => {
      const filesWithEnzymeImports = scanResults.filter(
        r => r.error === null && r.matches.length > 0
      );

      if (filesWithEnzymeImports.length > 0) {
        const report = filesWithEnzymeImports
          .map(r => {
            const matchDetails = r.matches
              .map(m => `    Line ${m.line}: [${m.package}] ${m.statement}`)
              .join('\n');
            return `  File: ${r.filePath}\n${matchDetails}`;
          })
          .join('\n\n');

        fail(
          `Found Enzyme imports in ${filesWithEnzymeImports.length} file(s):\n\n${report}\n\n` +
          `Please migrate these files to @testing-library/react.`
        );
      }

      expect(