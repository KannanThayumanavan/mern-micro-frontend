const fs = require('fs');
const path = require('path');

describe('package.json dependency migration: Enzyme → React Testing Library', () => {
  let packageJson;
  let devDependencies;
  let dependencies;

  beforeAll(() => {
    const packageJsonPath = path.resolve(__dirname, '../../package.json');

    if (!fs.existsSync(packageJsonPath)) {
      throw new Error(
        `package.json not found at expected path: ${packageJsonPath}`
      );
    }

    const rawContent = fs.readFileSync(packageJsonPath, 'utf8');

    try {
      packageJson = JSON.parse(rawContent);
    } catch (err) {
      throw new Error(`package.json is not valid JSON: ${err.message}`);
    }

    devDependencies = packageJson.devDependencies || {};
    dependencies = packageJson.dependencies || {};
  });

  // ---------------------------------------------------------------------------
  // Enzyme packages must be ABSENT
  // ---------------------------------------------------------------------------

  describe('Enzyme packages are removed', () => {
    const enzymePackages = [
      'enzyme',
      'enzyme-adapter-react-16',
      '@wojtekmaj/enzyme-adapter-react-17',
      'enzyme-to-json',
    ];

    enzymePackages.forEach((pkg) => {
      it(`devDependencies must NOT contain "${pkg}"`, () => {
        expect(devDependencies).not.toHaveProperty(pkg);
      });

      it(`dependencies must NOT contain "${pkg}"`, () => {
        expect(dependencies).not.toHaveProperty(pkg);
      });
    });
  });

  // ---------------------------------------------------------------------------
  // React Testing Library packages must be PRESENT with valid version ranges
  // ---------------------------------------------------------------------------

  describe('@testing-library/react is present with a valid version range', () => {
    it('exists in devDependencies', () => {
      expect(devDependencies).toHaveProperty('@testing-library/react');
    });

    it('has a non-empty version string', () => {
      const version = devDependencies['@testing-library/react'];
      expect(typeof version).toBe('string');
      expect(version.trim().length).toBeGreaterThan(0);
    });

    it('version range is semver-compatible (starts with ^, ~, >=, or a digit)', () => {
      const version = devDependencies['@testing-library/react'];
      expect(version).toMatch(/^(\^|~|>=|>|<=|<|\d)/);
    });

    it('major version is 12 or higher (React 17/18 compatible)', () => {
      const version = devDependencies['@testing-library/react'];
      const majorMatch = version.match(/(\d+)\./);
      if (majorMatch) {
        const major = parseInt(majorMatch[1], 10);
        expect(major).toBeGreaterThanOrEqual(12);
      }
    });
  });

  describe('@testing-library/jest-dom is present with a valid version range', () => {
    it('exists in devDependencies', () => {
      expect(devDependencies).toHaveProperty('@testing-library/jest-dom');
    });

    it('has a non-empty version string', () => {
      const version = devDependencies['@testing-library/jest-dom'];
      expect(typeof version).toBe('string');
      expect(version.trim().length).toBeGreaterThan(0);
    });

    it('version range is semver-compatible (starts with ^, ~, >=, or a digit)', () => {
      const version = devDependencies['@testing-library/jest-dom'];
      expect(version).toMatch(/^(\^|~|>=|>|<=|<|\d)/);
    });

    it('major version is 4 or higher', () => {
      const version = devDependencies['@testing-library/jest-dom'];
      const majorMatch = version.match(/(\d+)\./);
      if (majorMatch) {
        const major = parseInt(majorMatch[1], 10);
        expect(major).toBeGreaterThanOrEqual(4);
      }
    });
  });

  describe('@testing-library/user-event is present with a valid version range', () => {
    it('exists in devDependencies', () => {
      expect(devDependencies).toHaveProperty('@testing-library/user-event');
    });

    it('has a non-empty version string', () => {
      const version = devDependencies['@testing-library/user-event'];
      expect(typeof version).toBe('string');
      expect(version.trim().length).toBeGreaterThan(0);
    });

    it('version range is semver-compatible (starts with ^, ~, >=, or a digit)', () => {
      const version = devDependencies['@testing-library/user-event'];
      expect(version).toMatch(/^(\^|~|>=|>|<=|<|\d)/);
    });

    it('major version is 13 or higher', () => {
      const version = devDependencies['@testing-library/user-event'];
      const majorMatch = version.match(/(\d+)\./);
      if (majorMatch) {
        const major = parseInt(majorMatch[1], 10);
        expect(major).toBeGreaterThanOrEqual(13);
      }
    });
  });

  describe('@testing-library/react-hooks is present with a valid version range', () => {
    it('exists in devDependencies', () => {
      expect(devDependencies).toHaveProperty('@testing-library/react-hooks');
    });

    it('has a non-empty version string', () => {
      const version = devDependencies['@testing-library/react-hooks'];
      expect(typeof version).toBe('string');
      expect(version.trim().length).toBeGreaterThan(0);
    });

    it('version range is semver-compatible (starts with ^, ~, >=, or a digit)', () => {
      const version = devDependencies['@testing-library/react-hooks'];
      expect(version).toMatch(/^(\^|~|>=|>|<=|<|\d)/);
    });

    it('major version is 3 or higher', () => {
      const version = devDependencies['@testing-library/react-hooks'];
      const majorMatch = version.match(/(\d+)\./);
      if (majorMatch) {
        const major = parseInt(majorMatch[1], 10);
        expect(major).toBeGreaterThanOrEqual(3);
      }
    });
  });

  // ---------------------------------------------------------------------------
  // Structural sanity checks on package.json itself
  // ---------------------------------------------------------------------------

  describe('package.json structural integrity', () => {
    it('has a "name" field', () => {
      expect(packageJson).toHaveProperty('name');
      expect(typeof packageJson.name).toBe('string');
      expect(packageJson.name.trim().length).toBeGreaterThan(0);
    });

    it('has a "version" field', () => {
      expect(packageJson).toHaveProperty('version');
      expect(typeof packageJson.version).toBe('string');
    });

    it('devDependencies is an object', () => {
      expect(typeof devDependencies).toBe('object');
      expect(Array.isArray(devDependencies)).toBe(false);
    });

    it('all devDependency values are strings', () => {
      Object.entries(devDependencies).forEach(([pkg, version]) => {
        expect(typeof version).toBe('string');
        expect(version.trim().length).toBeGreaterThan(0);
      });
    });

    it('no devDependency version is set to an empty string', () => {
      Object.entries(devDependencies).forEach(([pkg, version]) => {
        expect(version.trim()).not.toBe('');
      });
    });
  });

  // ---------------------------------------------------------------------------
  // Cross-field consistency: RTL packages should not appear in prod dependencies