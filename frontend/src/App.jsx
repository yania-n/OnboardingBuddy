import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import AdminPortal from './components/admin/AdminPortal';
import JoinerPortal from './components/joiner/JoinerPortal';
import JoinerFormModal from './components/admin/JoinerFormModal';
import PlanEditorModal from './components/admin/PlanEditorModal';
import OrgScannerModal from './components/admin/OrgScannerModal';
import LearningPlansModal from './components/admin/LearningPlansModal';
import MissingFeedbackModal from './components/admin/MissingFeedbackModal';
import DocumentViewerModal from './components/DocumentViewerModal';
import ChatbotDrawer from './components/ChatbotDrawer';
import { fetchJoiners, fetchMissingFeedback } from './api/client';
import { Sparkles, Bot, MessageSquare } from 'lucide-react';

export default function App() {
  const [currentView, setCurrentView] = useState('joiner'); // 'manager' | 'joiner'
  const [joiners, setJoiners] = useState([]);
  const [selectedJoiner, setSelectedJoiner] = useState(null);
  const [missingFeedbackCount, setMissingFeedbackCount] = useState(0);

  // Modals state
  const [isJoinerFormOpen, setIsJoinerFormOpen] = useState(false);
  const [isPlanEditorOpen, setIsPlanEditorOpen] = useState(false);
  const [pendingJoinerData, setPendingJoinerData] = useState(null);
  const [previewPlanData, setPreviewPlanData] = useState(null);

  const [isOrgScannerOpen, setIsOrgScannerOpen] = useState(false);
  const [isLearningPlansOpen, setIsLearningPlansOpen] = useState(false);
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);
  const [activeDocRef, setActiveDocRef] = useState(null);

  // Chatbot toggle
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [joinerList, feedbackList] = await Promise.all([
        fetchJoiners(),
        fetchMissingFeedback()
      ]);
      setJoiners(joinerList);
      if (joinerList.length > 0 && !selectedJoiner) {
        setSelectedJoiner(joinerList[0]);
      }
      const pendingFeedback = (feedbackList || []).filter((f) => f.status === 'pending').length;
      setMissingFeedbackCount(pendingFeedback);
    } catch (e) {
      console.error(e);
    }
  };

  const handleOpenPlanEditor = (joinerFormData, planData) => {
    setPendingJoinerData(joinerFormData);
    setPreviewPlanData(planData);
    setIsJoinerFormOpen(false);
    setIsPlanEditorOpen(true);
  };

  const handlePlanPublished = async (newJoiner) => {
    await loadInitialData();
    setSelectedJoiner(newJoiner);
    setCurrentView('joiner');
  };

  const handleJoinerCreated = async (newJoiner) => {
    await loadInitialData();
    setSelectedJoiner(newJoiner);
    setCurrentView('joiner');
  };

  const handleSwitchToJoinerView = (joiner) => {
    setSelectedJoiner(joiner);
    setCurrentView('joiner');
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      
      {/* Top Navigation */}
      <Navbar
        currentView={currentView}
        setCurrentView={setCurrentView}
        joiners={joiners}
        selectedJoiner={selectedJoiner}
        setSelectedJoiner={setSelectedJoiner}
        onOpenJoinerForm={() => setIsJoinerFormOpen(true)}
        onOpenOrgScanner={() => setIsOrgScannerOpen(true)}
        onOpenLearningPlans={() => setIsLearningPlansOpen(true)}
        onOpenFeedback={() => setIsFeedbackOpen(true)}
        missingCount={missingFeedbackCount}
      />

      {/* Main App Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'manager' ? (
          <AdminPortal
            onOpenJoinerForm={() => setIsJoinerFormOpen(true)}
            onSelectJoinerForPlan={(j) => setSelectedJoiner(j)}
            onSwitchToJoinerView={handleSwitchToJoinerView}
          />
        ) : (
          <JoinerPortal
            selectedJoiner={selectedJoiner}
            onOpenDoc={(ref) => setActiveDocRef(ref)}
            onOpenChatbot={() => setIsChatbotOpen(!isChatbotOpen)}
            isChatbotOpen={isChatbotOpen}
          />
        )}
      </main>

      {/* Floating Chatbot Toggle Button (When drawer is closed) */}
      {!isChatbotOpen && (
        <button
          onClick={() => setIsChatbotOpen(true)}
          className="fixed bottom-6 right-6 z-30 flex items-center gap-2.5 px-4 py-3 bg-slate-900 hover:bg-brand-600 text-white rounded-full shadow-2xl hover:shadow-brand-500/25 transition-all hover:scale-105 active:scale-95 group"
        >
          <div className="w-7 h-7 rounded-full bg-brand-500 flex items-center justify-center text-white">
            <Sparkles className="w-4 h-4" />
          </div>
          <span className="text-xs font-bold pr-1">Ask AI Buddy</span>
        </button>
      )}

      {/* Floating Grounded Q&A Chatbot Drawer */}
      {isChatbotOpen && (
        <ChatbotDrawer
          selectedJoiner={selectedJoiner}
          onOpenDoc={(ref) => setActiveDocRef(ref)}
          onClose={() => setIsChatbotOpen(false)}
        />
      )}

      {/* MODALS */}

      {/* 1. New Joiner Form Modal */}
      {isJoinerFormOpen && (
        <JoinerFormModal
          onClose={() => setIsJoinerFormOpen(false)}
          onJoinerCreated={handleJoinerCreated}
          onOpenPlanEditor={handleOpenPlanEditor}
        />
      )}

      {/* 2. AI Plan Review & Editor Modal */}
      {isPlanEditorOpen && pendingJoinerData && previewPlanData && (
        <PlanEditorModal
          joinerData={pendingJoinerData}
          previewPlanData={previewPlanData}
          onClose={() => setIsPlanEditorOpen(false)}
          onPlanPublished={handlePlanPublished}
        />
      )}

      {/* 3. Org Expert Knowledge & Scan Modal */}
      {isOrgScannerOpen && (
        <OrgScannerModal onClose={() => setIsOrgScannerOpen(false)} />
      )}

      {/* 4. Learning Plans (.md) Repository Modal */}
      {isLearningPlansOpen && (
        <LearningPlansModal onClose={() => setIsLearningPlansOpen(false)} />
      )}

      {/* 5. Missing Feedback Center Modal */}
      {isFeedbackOpen && (
        <MissingFeedbackModal
          onClose={() => setIsFeedbackOpen(false)}
          onFeedbackUpdated={loadInitialData}
        />
      )}

      {/* 6. In-App Knowledge Base Document Viewer */}
      {activeDocRef && (
        <DocumentViewerModal
          docRef={activeDocRef}
          onClose={() => setActiveDocRef(null)}
        />
      )}

    </div>
  );
}
