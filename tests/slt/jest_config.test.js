const fs = require('fs');
const path = require('path');

describe('jest.config.js validation', () => {
  let jestConfig;
  let jestConfigRaw;
  let jestConfigPath;

  beforeAll(() => {
    jestConfigPath = path.resolve(__dirname, '../../jest.config.js');

    if (!fs.existsSync(jestConfigPath)) {
      throw new Error(`jest.config.js not found at path: ${jestConfigPath}`);
    }

    jestConfigRaw = fs.readFileSync(jestConfigPath, 'utf8');

    try {
      jestConfig = require(jestConfigPath);
    } catch (err) {
      throw new Error(`Failed to require jest.config.js: ${err.message}`);
    }
  });

  describe('testEnvironment', () => {
    test('should have testEnvironment defined', () => {
      expect(jestConfig).toHaveProperty('testEnvironment');
    });

    test('testEnvironment should be set to jsdom', () => {
      const env = jestConfig.testEnvironment;
      const validJsdomValues = ['jsdom', 'jest-environment-jsdom'];
      expect(validJsdomValues).toContain(env);
    });

    test('testEnvironment should not be node', () => {
      expect(jestConfig.testEnvironment).not.toBe('node');
    });

    test('testEnvironment should not be undefined or null', () => {
      expect(jestConfig.testEnvironment).toBeTruthy();
    });
  });

  describe('setupFilesAfterFramework / setupFiles', () => {
    test('should have setupFilesAfterFramework or setupFiles defined', () => {
      const hasSetupFilesAfterFramework = jestConfig.hasOwnProperty('setupFilesAfterFramework');
      const hasSetupFiles = jestConfig.hasOwnProperty('setupFiles');
      const hasSetupFilesAfterFrameworkAlias = jestConfig.hasOwnProperty('setupFilesAfterFramework');
      const hasAnySetup =
        jestConfig.hasOwnProperty('setupFilesAfterFramework') ||
        jestConfig.hasOwnProperty('setupFiles') ||
        jestConfig.hasOwnProperty('setupFilesAfterFramework');

      const setupFilesAfterFramework = jestConfig.setupFilesAfterFramework;
      const setupFiles = jestConfig.setupFiles;
      const setupFilesAfterFrameworkValue = jestConfig.setupFilesAfterFramework;

      const allSetupEntries = [
        ...(Array.isArray(jestConfig.setupFilesAfterFramework) ? jestConfig.setupFilesAfterFramework : []),
        ...(Array.isArray(jestConfig.setupFiles) ? jestConfig.setupFiles : []),
        ...(Array.isArray(jestConfig.setupFilesAfterFramework) ? jestConfig.setupFilesAfterFramework : []),
      ];

      const hasSetupFilesAfterFrameworkKey = 'setupFilesAfterFramework' in jestConfig;
      const hasSetupFilesKey = 'setupFiles' in jestConfig;

      expect(
        hasSetupFilesAfterFrameworkKey || hasSetupFilesKey
      ).toBe(true);
    });

    test('setup file entries should be an array', () => {
      const setupFilesAfterFramework = jestConfig.setupFilesAfterFramework;
      const setupFiles = jestConfig.setupFiles;

      if (setupFilesAfterFramework !== undefined) {
        expect(Array.isArray(setupFilesAfterFramework)).toBe(true);
      }

      if (setupFiles !== undefined) {
        expect(Array.isArray(setupFiles)).toBe(true);
      }
    });

    test('should reference a setup file (e.g., setupTests.js or jest.setup.js)', () => {
      const allSetupEntries = [
        ...(Array.isArray(jestConfig.setupFilesAfterFramework) ? jestConfig.setupFilesAfterFramework : []),
        ...(Array.isArray(jestConfig.setupFiles) ? jestConfig.setupFiles : []),
      ];

      expect(allSetupEntries.length).toBeGreaterThan(0);

      const hasValidSetupFile = allSetupEntries.some((entry) => {
        const normalized = entry.replace(/\\/g, '/');
        return (
          normalized.includes('setupTests') ||
          normalized.includes('jest.setup') ||
          normalized.includes('setup') ||
          normalized.match(/\.(js|ts|jsx|tsx)$/)
        );
      });

      expect(hasValidSetupFile).toBe(true);
    });

    test('setup file path should not be empty string', () => {
      const allSetupEntries = [
        ...(Array.isArray(jestConfig.setupFilesAfterFramework) ? jestConfig.setupFilesAfterFramework : []),
        ...(Array.isArray(jestConfig.setupFiles) ? jestConfig.setupFiles : []),
      ];

      allSetupEntries.forEach((entry) => {
        expect(typeof entry).toBe('string');
        expect(entry.trim().length).toBeGreaterThan(0);
      });
    });
  });

  describe('Enzyme-specific configuration absence', () => {
    test('should not contain enzyme-to-json/serializer in snapshotSerializers', () => {
      const serializers = jestConfig.snapshotSerializers;

      if (serializers !== undefined) {
        expect(Array.isArray(serializers)).toBe(true);
        const hasEnzymeSerializer = serializers.some((s) =>
          s.includes('enzyme-to-json')
        );
        expect(hasEnzymeSerializer).toBe(false);
      } else {
        expect(serializers).toBeUndefined();
      }
    });

    test('raw config file should not contain enzyme-to-json/serializer string', () => {
      expect(jestConfigRaw).not.toContain('enzyme-to-json/serializer');
    });

    test('raw config file should not contain enzyme-to-json', () => {
      expect(jestConfigRaw).not.toContain('enzyme-to-json');
    });

    test('should not contain Enzyme-specific transform configuration', () => {
      const transform = jestConfig.transform;

      if (transform !== undefined) {
        const transformValues = Object.values(transform);
        const hasEnzymeTransform = transformValues.some((val) => {
          if (typeof val === 'string') {
            return val.includes('enzyme');
          }
          if (Array.isArray(val)) {
            return val.some((v) => typeof v === 'string' && v.includes('enzyme'));
          }
          return false;
        });
        expect(hasEnzymeTransform).toBe(false);
      }
    });

    test('raw config file should not reference enzyme adapter', () => {
      expect(jestConfigRaw).not.toMatch(/enzyme-adapter-react/i);
    });

    test('raw config file should not reference Enzyme setup in globals', () => {
      expect(jestConfigRaw).not.toMatch(/Enzyme\.configure/);
    });

    test('snapshotSerializers should not include any enzyme-related serializer', () => {
      const serializers = jestConfig.snapshotSerializers || [];
      serializers.forEach((serializer) => {
        expect(serializer.toLowerCase()).not.toContain('enzyme');
      });
    });

    test('globals configuration should not contain enzyme-specific settings', () => {
      const globals = jestConfig.globals;

      if (globals !== undefined) {
        const globalsStr = JSON.stringify(globals);
        expect(globalsStr.toLowerCase()).not.toContain('enzyme');
      }
    });
  });

  describe('Overall config structure integrity', () => {
    test('jest