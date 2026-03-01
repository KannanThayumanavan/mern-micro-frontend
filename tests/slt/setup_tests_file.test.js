const fs = require('fs');
const path = require('path');

describe('Jest Setup File Verification', () => {
  let setupFileContent = null;
  let setupFilePath = null;
  let setupFileName = null;

  beforeAll(() => {
    const possibleSetupFiles = [
      'setupTests.js',
      'jest.setup.js',
      'setupTests.ts',
      'jest.setup.ts',
      'src/setupTests.js',
      'src/jest.setup.js',
      'src/setupTests.ts',
      'src/jest.setup.ts',
    ];

    const projectRoot = path.resolve(__dirname, '../../');

    for (const fileName of possibleSetupFiles) {
      const fullPath = path.join(projectRoot, fileName);
      if (fs.existsSync(fullPath)) {
        setupFilePath = fullPath;
        setupFileName = fileName;
        setupFileContent = fs.readFileSync(fullPath, 'utf8');
        break;
      }
    }
  });

  describe('Setup File Existence', () => {
    test('should find a Jest setup file (setupTests.js or jest.setup.js)', () => {
      expect(setupFilePath).not.toBeNull();
      expect(setupFileContent).not.toBeNull();
    });

    test('setup file should not be empty', () => {
      expect(setupFileContent).toBeTruthy();
      expect(setupFileContent.trim().length).toBeGreaterThan(0);
    });
  });

  describe('Enzyme - Must NOT be present', () => {
    test('should not import enzyme', () => {
      if (!setupFileContent) return;
      const enzymeImportPatterns = [
        /require\s*\(\s*['"]enzyme['"]\s*\)/,
        /from\s+['"]enzyme['"]/,
        /import\s+.*enzyme/i,
      ];
      enzymeImportPatterns.forEach((pattern) => {
        expect(setupFileContent).not.toMatch(pattern);
      });
    });

    test('should not import enzyme-adapter-react-16', () => {
      if (!setupFileContent) return;
      const adapterPatterns = [
        /require\s*\(\s*['"]enzyme-adapter-react-16['"]\s*\)/,
        /from\s+['"]enzyme-adapter-react-16['"]/,
        /import\s+.*enzyme-adapter-react-16/i,
      ];
      adapterPatterns.forEach((pattern) => {
        expect(setupFileContent).not.toMatch(pattern);
      });
    });

    test('should not import enzyme-adapter-react-17', () => {
      if (!setupFileContent) return;
      const adapterPatterns = [
        /require\s*\(\s*['"]enzyme-adapter-react-17['"]\s*\)/,
        /from\s+['"]enzyme-adapter-react-17['"]/,
        /import\s+.*enzyme-adapter-react-17/i,
      ];
      adapterPatterns.forEach((pattern) => {
        expect(setupFileContent).not.toMatch(pattern);
      });
    });

    test('should not configure Enzyme via Enzyme.configure()', () => {
      if (!setupFileContent) return;
      const configurePatterns = [
        /Enzyme\.configure\s*\(/,
        /enzyme\.configure\s*\(/,
        /configure\s*\(\s*\{\s*adapter/,
      ];
      configurePatterns.forEach((pattern) => {
        expect(setupFileContent).not.toMatch(pattern);
      });
    });

    test('should not reference any Enzyme adapter in any form', () => {
      if (!setupFileContent) return;
      const adapterReferencePatterns = [
        /new\s+Adapter\s*\(\s*\)/,
        /new\s+EnzymeAdapter\s*\(\s*\)/,
        /adapter\s*:\s*new/i,
      ];
      adapterReferencePatterns.forEach((pattern) => {
        expect(setupFileContent).not.toMatch(pattern);
      });
    });

    test('should not import any enzyme-related package', () => {
      if (!setupFileContent) return;
      const enzymeRelatedPattern = /['"]enzyme[^'"]*['"]/g;
      const matches = setupFileContent.match(enzymeRelatedPattern) || [];
      const enzymeMatches = matches.filter((m) =>
        m.toLowerCase().includes('enzyme')
      );
      expect(enzymeMatches).toHaveLength(0);
    });
  });

  describe('@testing-library/jest-dom - Must be imported', () => {
    test('should import @testing-library/jest-dom', () => {
      if (!setupFileContent) return;
      const jestDomPatterns = [
        /require\s*\(\s*['"]@testing-library\/jest-dom['"]\s*\)/,
        /from\s+['"]@testing-library\/jest-dom['"]/,
        /import\s+['"]@testing-library\/jest-dom['"]/,
        /import\s+.*from\s+['"]@testing-library\/jest-dom['"]/,
      ];
      const hasJestDomImport = jestDomPatterns.some((pattern) =>
        pattern.test(setupFileContent)
      );
      expect(hasJestDomImport).toBe(true);
    });

    test('should not use deprecated extend-expect import path', () => {
      if (!setupFileContent) return;
      const deprecatedPattern =
        /@testing-library\/jest-dom\/extend-expect/;
      expect(setupFileContent).not.toMatch(deprecatedPattern);
    });
  });

  describe('globalThis.IS_REACT_ACT_ENVIRONMENT - Must be set to true', () => {
    test('should set globalThis.IS_REACT_ACT_ENVIRONMENT to true', () => {
      if (!setupFileContent) return;
      const reactActPatterns = [
        /globalThis\s*\.\s*IS_REACT_ACT_ENVIRONMENT\s*=\s*true/,
        /globalThis\s*\[\s*['"]IS_REACT_ACT_ENVIRONMENT['"]\s*\]\s*=\s*true/,
      ];
      const hasReactActEnv = reactActPatterns.some((pattern) =>
        pattern.test(setupFileContent)
      );
      expect(hasReactActEnv).toBe(true);
    });

    test('should not set IS_REACT_ACT_ENVIRONMENT to false', () => {
      if (!setupFileContent) return;
      const falsePattern =
        /globalThis\s*\.\s*IS_REACT_ACT_ENVIRONMENT\s*=\s*false/;
      expect(setupFileContent).not.toMatch(falsePattern);
    });

    test('should not set IS_REACT_ACT_ENVIRONMENT to a non-boolean truthy string', () => {
      if (!setupFileContent) return;
      const stringPattern =
        /globalThis\s*\.\s*IS_REACT_ACT_ENVIRONMENT\s*=\s*['"][^'"]+['"]/;
      expect(setupFileContent).not.toMatch(stringPattern);
    });
  });

  describe('Combined Requirements Validation', () => {
    test('setup file satisfies all three requirements simultaneously', () => {
      if (!setupFileContent) {
        fail('No setup file found');
        return;
      }

      const hasNoEnzyme = !/enzyme/i.test(setupFileContent);

      const hasJestDom =
        /require\s*\(\s*['"]@testing-library\/jest-dom['"]\s*\)/.test(
          setupFileContent
        ) ||
        /from\s+['"]@testing-library\/jest-dom['"]/i.test(setupFileContent) ||
        /