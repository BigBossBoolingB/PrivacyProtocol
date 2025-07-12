import Layout from "./Layout.jsx";

import Dashboard from "./Dashboard";

import Analyzer from "./Analyzer";

import Profile from "./Profile";

import History from "./History";

import Insights from "./Insights";

import PolicyTracker from "./PolicyTracker";

import AdvancedInsights from "./AdvancedInsights";

import { BrowserRouter as Router, Route, Routes, useLocation } from 'react-router-dom';

const PAGES = {
    
    Dashboard: Dashboard,
    
    Analyzer: Analyzer,
    
    Profile: Profile,
    
    History: History,
    
    Insights: Insights,
    
    PolicyTracker: PolicyTracker,
    
    AdvancedInsights: AdvancedInsights,
    
}

function _getCurrentPage(url) {
    if (url.endsWith('/')) {
        url = url.slice(0, -1);
    }
    let urlLastPart = url.split('/').pop();
    if (urlLastPart.includes('?')) {
        urlLastPart = urlLastPart.split('?')[0];
    }

    const pageName = Object.keys(PAGES).find(page => page.toLowerCase() === urlLastPart.toLowerCase());
    return pageName || Object.keys(PAGES)[0];
}

// Create a wrapper component that uses useLocation inside the Router context
function PagesContent() {
    const location = useLocation();
    const currentPage = _getCurrentPage(location.pathname);
    
    return (
        <Layout currentPageName={currentPage}>
            <Routes>            
                
                    <Route path="/" element={<Dashboard />} />
                
                
                <Route path="/Dashboard" element={<Dashboard />} />
                
                <Route path="/Analyzer" element={<Analyzer />} />
                
                <Route path="/Profile" element={<Profile />} />
                
                <Route path="/History" element={<History />} />
                
                <Route path="/Insights" element={<Insights />} />
                
                <Route path="/PolicyTracker" element={<PolicyTracker />} />
                
                <Route path="/AdvancedInsights" element={<AdvancedInsights />} />
                
            </Routes>
        </Layout>
    );
}

export default function Pages() {
    return (
        <Router>
            <PagesContent />
        </Router>
    );
}