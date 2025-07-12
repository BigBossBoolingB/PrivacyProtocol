/**
 * Unit tests for utility functions
 */

// Import utilities to test
import { 
  createPageUrl, 
  cn, 
  sleep, 
  uuidv4, 
  isEmpty, 
  deepClone 
} from '../../src/utils/index.ts';

// createPageUrl tests
describe('createPageUrl', () => {
  test('converts page name to URL format', () => {
    expect(createPageUrl('Home Page')).toBe('/home-page');
    expect(createPageUrl('User Profile')).toBe('/user-profile');
    expect(createPageUrl('PRIVACY POLICY')).toBe('/privacy-policy');
  });
});

// cn (classname utility) tests
describe('cn', () => {
  test('combines class names correctly', () => {
    expect(cn('btn', 'btn-primary')).toBe('btn btn-primary');
    expect(cn('card', false && 'hidden', null, undefined, 'p-4')).toBe('card p-4');
    expect(cn('menu', true && 'active')).toBe('menu active');
  });
});

// isEmpty tests
describe('isEmpty', () => {
  test('correctly identifies empty values', () => {
    expect(isEmpty(null)).toBe(true);
    expect(isEmpty(undefined)).toBe(true);
    expect(isEmpty('')).toBe(true);
    expect(isEmpty('  ')).toBe(true);
    expect(isEmpty([])).toBe(true);
    expect(isEmpty({})).toBe(true);
    
    expect(isEmpty('text')).toBe(false);
    expect(isEmpty([1, 2])).toBe(false);
    expect(isEmpty({ key: 'value' })).toBe(false);
    expect(isEmpty(0)).toBe(false);
    expect(isEmpty(false)).toBe(false);
  });
});

// deepClone tests
describe('deepClone', () => {
  test('creates a deep copy of objects', () => {
    const original = { 
      name: 'Test', 
      settings: { 
        active: true, 
        theme: 'dark' 
      },
      tags: ['privacy', 'security']
    };
    
    const clone = deepClone(original);
    
    // Should be equal in value
    expect(clone).toEqual(original);
    
    // But not the same reference
    expect(clone).not.toBe(original);
    expect(clone.settings).not.toBe(original.settings);
    expect(clone.tags).not.toBe(original.tags);
    
    // Modifying clone should not affect original
    clone.name = 'Modified';
    clone.settings.active = false;
    clone.tags.push('modified');
    
    expect(original.name).toBe('Test');
    expect(original.settings.active).toBe(true);
    expect(original.tags).toHaveLength(2);
  });
  
  test('handles primitive values', () => {
    expect(deepClone(42)).toBe(42);
    expect(deepClone('string')).toBe('string');
    expect(deepClone(null)).toBe(null);
  });
});

// uuidv4 tests
describe('uuidv4', () => {
  test('generates a valid UUID v4 string', () => {
    const uuid = uuidv4();
    expect(typeof uuid).toBe('string');
    expect(uuid).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
  });
  
  test('generates unique UUIDs', () => {
    const uuids = new Set();
    for (let i = 0; i < 100; i++) {
      uuids.add(uuidv4());
    }
    expect(uuids.size).toBe(100);
  });
});

// sleep tests
describe('sleep', () => {
  test('resolves after the specified time', async () => {
    const start = Date.now();
    await sleep(100);
    const duration = Date.now() - start;
    expect(duration).toBeGreaterThanOrEqual(90); // Allow for small timing variations
  });
});