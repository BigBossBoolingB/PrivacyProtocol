self.onmessage = function(e) {
  const { type, data } = e.data;
  
  switch (type) {
    case 'ANALYZE_POLICY':
      analyzePolicyText(data);
      break;
    case 'CALCULATE_RISK_SCORE':
      calculateRiskScore(data);
      break;
    case 'EXTRACT_CLAUSES':
      extractClauses(data);
      break;
    default:
      self.postMessage({ type: 'ERROR', error: 'Unknown task type' });
  }
};

function analyzePolicyText(policyData) {
  try {
    const { text, options = {} } = policyData;
    
    const analysis = {
      wordCount: text.split(/\s+/).length,
      readabilityScore: calculateReadabilityScore(text),
      keyTerms: extractKeyTerms(text),
      dataCollectionPatterns: findDataCollectionPatterns(text),
      riskIndicators: identifyRiskIndicators(text),
      timestamp: Date.now()
    };
    
    self.postMessage({
      type: 'ANALYSIS_COMPLETE',
      result: analysis
    });
  } catch (error) {
    self.postMessage({
      type: 'ERROR',
      error: error.message
    });
  }
}

function calculateRiskScore(scoreData) {
  try {
    const { clauses, userProfile = {} } = scoreData;
    
    let totalScore = 0;
    const weights = {
      dataCollection: 0.3,
      dataSharing: 0.25,
      dataRetention: 0.2,
      userRights: 0.15,
      security: 0.1
    };
    
    clauses.forEach(clause => {
      const categoryWeight = weights[clause.category] || 0.1;
      const riskLevel = clause.riskLevel || 1;
      totalScore += riskLevel * categoryWeight * 100;
    });
    
    const adjustedScore = Math.min(100, Math.max(0, totalScore));
    
    self.postMessage({
      type: 'RISK_SCORE_COMPLETE',
      result: {
        score: adjustedScore,
        breakdown: calculateScoreBreakdown(clauses, weights),
        recommendations: generateRecommendations(adjustedScore, clauses)
      }
    });
  } catch (error) {
    self.postMessage({
      type: 'ERROR',
      error: error.message
    });
  }
}

function extractClauses(extractionData) {
  try {
    const { text } = extractionData;
    
    const clauses = [];
    const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
    
    sentences.forEach((sentence, index) => {
      const trimmed = sentence.trim();
      if (trimmed.length < 20) return;
      
      const riskKeywords = [
        'collect', 'share', 'sell', 'transfer', 'store', 'retain',
        'third party', 'partner', 'affiliate', 'advertiser'
      ];
      
      const hasRiskKeyword = riskKeywords.some(keyword => 
        trimmed.toLowerCase().includes(keyword)
      );
      
      if (hasRiskKeyword) {
        clauses.push({
          id: `clause_${index}`,
          text: trimmed,
          category: categorizeClause(trimmed),
          riskLevel: assessClauseRisk(trimmed),
          position: index
        });
      }
    });
    
    self.postMessage({
      type: 'CLAUSES_EXTRACTED',
      result: clauses
    });
  } catch (error) {
    self.postMessage({
      type: 'ERROR',
      error: error.message
    });
  }
}

function calculateReadabilityScore(text) {
  const sentences = text.split(/[.!?]+/).length;
  const words = text.split(/\s+/).length;
  const syllables = countSyllables(text);
  
  const avgWordsPerSentence = words / sentences;
  const avgSyllablesPerWord = syllables / words;
  
  const fleschScore = 206.835 - (1.015 * avgWordsPerSentence) - (84.6 * avgSyllablesPerWord);
  return Math.max(0, Math.min(100, fleschScore));
}

function countSyllables(text) {
  return text.toLowerCase()
    .replace(/[^a-z]/g, '')
    .replace(/[aeiou]{2,}/g, 'a')
    .replace(/[^aeiou]/g, '')
    .length || 1;
}

function extractKeyTerms(text) {
  const commonTerms = [
    'personal information', 'data collection', 'third party',
    'cookies', 'tracking', 'analytics', 'advertising',
    'user rights', 'opt out', 'delete', 'access'
  ];
  
  return commonTerms.filter(term => 
    text.toLowerCase().includes(term)
  );
}

function findDataCollectionPatterns(text) {
  const patterns = [
    /collect[s]?\s+(?:your\s+)?(?:personal\s+)?(?:information|data)/gi,
    /gather[s]?\s+(?:information|data)/gi,
    /obtain[s]?\s+(?:information|data)/gi,
    /receive[s]?\s+(?:information|data)/gi
  ];
  
  const matches = [];
  patterns.forEach(pattern => {
    const found = text.match(pattern);
    if (found) {
      matches.push(...found);
    }
  });
  
  return matches;
}

function identifyRiskIndicators(text) {
  const highRiskTerms = [
    'sell', 'monetize', 'third party', 'partner',
    'indefinitely', 'permanent', 'irrevocable'
  ];
  
  return highRiskTerms.filter(term => 
    text.toLowerCase().includes(term)
  );
}

function categorizeClause(text) {
  const categories = {
    dataCollection: ['collect', 'gather', 'obtain', 'receive'],
    dataSharing: ['share', 'disclose', 'provide', 'transfer'],
    dataRetention: ['retain', 'store', 'keep', 'maintain'],
    userRights: ['right', 'access', 'delete', 'opt out'],
    security: ['secure', 'protect', 'encrypt', 'safeguard']
  };
  
  const lowerText = text.toLowerCase();
  
  for (const [category, keywords] of Object.entries(categories)) {
    if (keywords.some(keyword => lowerText.includes(keyword))) {
      return category;
    }
  }
  
  return 'general';
}

function assessClauseRisk(text) {
  const highRiskTerms = ['sell', 'monetize', 'indefinitely', 'irrevocable'];
  const mediumRiskTerms = ['share', 'third party', 'partner', 'affiliate'];
  const lowRiskTerms = ['protect', 'secure', 'opt out', 'delete'];
  
  const lowerText = text.toLowerCase();
  
  if (highRiskTerms.some(term => lowerText.includes(term))) {
    return 3;
  } else if (mediumRiskTerms.some(term => lowerText.includes(term))) {
    return 2;
  } else if (lowRiskTerms.some(term => lowerText.includes(term))) {
    return 0.5;
  }
  
  return 1;
}

function calculateScoreBreakdown(clauses, weights) {
  const breakdown = {};
  
  Object.keys(weights).forEach(category => {
    const categoryScore = clauses
      .filter(clause => clause.category === category)
      .reduce((sum, clause) => sum + clause.riskLevel, 0);
    
    breakdown[category] = Math.min(100, categoryScore * weights[category] * 100);
  });
  
  return breakdown;
}

function generateRecommendations(score, clauses) {
  const recommendations = [];
  
  if (score > 70) {
    recommendations.push('This policy has high privacy risks. Consider limiting data sharing.');
  } else if (score > 40) {
    recommendations.push('This policy has moderate privacy risks. Review data collection practices.');
  } else {
    recommendations.push('This policy has relatively low privacy risks.');
  }
  
  const highRiskClauses = clauses.filter(clause => clause.riskLevel >= 3);
  if (highRiskClauses.length > 0) {
    recommendations.push(`Pay special attention to ${highRiskClauses.length} high-risk clauses.`);
  }
  
  return recommendations;
}
