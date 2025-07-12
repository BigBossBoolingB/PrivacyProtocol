class WebWorkerManager {
  constructor() {
    this.workers = new Map();
    this.taskQueue = [];
    this.maxWorkers = navigator.hardwareConcurrency || 4;
  }

  getWorker(workerName) {
    if (!this.workers.has(workerName)) {
      try {
        const worker = new Worker(`/src/workers/${workerName}.js`, { type: 'module' });
        this.workers.set(workerName, {
          worker,
          busy: false,
          tasks: 0
        });
      } catch (error) {
        console.error(`Failed to create worker ${workerName}:`, error);
        return null;
      }
    }
    
    return this.workers.get(workerName);
  }

  async executeTask(workerName, taskType, data, options = {}) {
    const { timeout = 30000 } = options;
    
    return new Promise((resolve, reject) => {
      const workerInfo = this.getWorker(workerName);
      
      if (!workerInfo) {
        reject(new Error(`Worker ${workerName} not available`));
        return;
      }

      const { worker } = workerInfo;
      const taskId = `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      const timeoutId = setTimeout(() => {
        worker.terminate();
        this.workers.delete(workerName);
        reject(new Error('Worker task timeout'));
      }, timeout);

      const messageHandler = (e) => {
        const { type, result, error } = e.data;
        
        if (type === 'ERROR') {
          clearTimeout(timeoutId);
          worker.removeEventListener('message', messageHandler);
          workerInfo.busy = false;
          reject(new Error(error));
        } else if (type.includes('COMPLETE') || type.includes('EXTRACTED')) {
          clearTimeout(timeoutId);
          worker.removeEventListener('message', messageHandler);
          workerInfo.busy = false;
          workerInfo.tasks++;
          resolve(result);
        }
      };

      worker.addEventListener('message', messageHandler);
      
      workerInfo.busy = true;
      worker.postMessage({
        type: taskType,
        data,
        taskId
      });
    });
  }

  async analyzePolicyText(text, options = {}) {
    return this.executeTask('analysisWorker', 'ANALYZE_POLICY', { text, options });
  }

  async calculateRiskScore(clauses, userProfile = {}) {
    return this.executeTask('analysisWorker', 'CALCULATE_RISK_SCORE', { clauses, userProfile });
  }

  async extractClauses(text) {
    return this.executeTask('analysisWorker', 'EXTRACT_CLAUSES', { text });
  }

  getWorkerStats() {
    const stats = {};
    
    this.workers.forEach((workerInfo, name) => {
      stats[name] = {
        busy: workerInfo.busy,
        tasksCompleted: workerInfo.tasks
      };
    });
    
    return stats;
  }

  terminateAll() {
    this.workers.forEach((workerInfo, name) => {
      workerInfo.worker.terminate();
    });
    this.workers.clear();
  }

  terminateWorker(workerName) {
    const workerInfo = this.workers.get(workerName);
    if (workerInfo) {
      workerInfo.worker.terminate();
      this.workers.delete(workerName);
    }
  }
}

const webWorkerManager = new WebWorkerManager();

export const analyzePolicyText = (text, options) => 
  webWorkerManager.analyzePolicyText(text, options);

export const calculateRiskScore = (clauses, userProfile) => 
  webWorkerManager.calculateRiskScore(clauses, userProfile);

export const extractClauses = (text) => 
  webWorkerManager.extractClauses(text);

export const getWorkerStats = () => 
  webWorkerManager.getWorkerStats();

export const terminateAllWorkers = () => 
  webWorkerManager.terminateAll();

export default webWorkerManager;
