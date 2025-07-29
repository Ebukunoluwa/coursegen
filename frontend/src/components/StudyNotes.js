import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  BookOpen, 
  FileText, 
  Edit3, 
  Download, 
  Save, 
  CheckCircle,
  Star,
  List,
  User,
  RefreshCw
} from 'lucide-react';
import { getStudyNotes, updateOwnNotes } from '../services/api';

const StudyNotes = () => {
  const { lessonId } = useParams();
  const navigate = useNavigate();
  const [notes, setNotes] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('golden');
  const [ownNotes, setOwnNotes] = useState('');
  const [saving, setSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState(null);
  const [regenerating, setRegenerating] = useState(false);
  const autoSaveRef = useRef(null);

  useEffect(() => {
    loadNotes();
  }, [lessonId]);

  const loadNotes = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getStudyNotes(lessonId);
      setNotes(data);
      setOwnNotes(data.own_notes || '');
      setLoading(false);
    } catch (err) {
      setError('Failed to load study notes');
      setLoading(false);
    }
  };

  const regenerateNotes = async () => {
    try {
      setRegenerating(true);
      setError(null);
      const data = await getStudyNotes(`${lessonId}?regenerate=true`);
      setNotes(data);
      setOwnNotes(data.own_notes || '');
      setRegenerating(false);
    } catch (err) {
      setError('Failed to regenerate study notes');
      setRegenerating(false);
    }
  };

  const handleOwnNotesChange = (e) => {
    const newValue = e.target.value;
    setOwnNotes(newValue);
    
    if (autoSaveRef.current) {
      clearTimeout(autoSaveRef.current);
    }
    
    autoSaveRef.current = setTimeout(() => {
      saveOwnNotes(newValue);
    }, 2000);
  };

  const saveOwnNotes = async (notesContent = ownNotes) => {
    try {
      setSaving(true);
      await updateOwnNotes(lessonId, { own_notes: notesContent });
      setLastSaved(new Date());
      setSaving(false);
    } catch (err) {
      setError('Failed to save notes');
      setSaving(false);
    }
  };

  const exportToPDF = () => {
    const content = `
STUDY NOTES - ${notes?.lesson?.title || 'Lesson'}
Generated on: ${new Date().toLocaleString()}

${notes?.content || ''}

GOLDEN NOTES:
${notes?.golden_notes_cards?.map((card, index) => `
${index + 1}. ${card.title}
   ${card.explanation}
   
   Examples:
   ${card.examples?.map(example => `   - ${example}`).join('\n') || '   No examples provided'}
   
   Key Points:
   ${card.key_points?.map(point => `   - ${point}`).join('\n') || '   No key points provided'}
`).join('\n') || 'No golden notes available'}

SUMMARIES:
${notes?.summaries_list?.map((summary, index) => `${index + 1}. ${summary}`).join('\n') || 'No summaries available'}

MY NOTES:
${ownNotes || 'No personal notes added yet.'}
    `;
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `study-notes-${lessonId}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const renderGoldenNotes = () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {notes?.golden_notes_cards?.length > 0 ? (
        notes.golden_notes_cards.map((card, index) => (
          <div key={index} className="mb-6">
            <h3 className="text-2xl font-bold text-gray-900 mb-3 leading-tight" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>{card.title}</h3>
            <p className="text-gray-700 leading-relaxed text-base" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>{card.explanation}</p>
            
            {card.examples && card.examples.length > 0 && (
              <div className="mt-4">
                <h4 className="font-semibold text-gray-900 mb-2 text-sm" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>Examples:</h4>
                <ul className="space-y-1 ml-3">
                  {card.examples.map((example, idx) => (
                    <li key={idx} className="text-gray-700 text-sm" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>
                      • {example}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {card.key_points && card.key_points.length > 0 && (
              <div className="mt-4">
                <h4 className="font-semibold text-gray-900 mb-2 text-sm" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>Key Points:</h4>
                <ul className="space-y-1 ml-3">
                  {card.key_points.map((point, idx) => (
                    <li key={idx} className="text-gray-700 text-sm" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>
                      • {point}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))
      ) : (
        <div className="text-center py-8 col-span-2">
          <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500 text-sm" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>No golden notes available yet.</p>
        </div>
      )}
    </div>
  );

  const renderSummaries = () => (
    <div className="space-y-4">
      {notes?.summaries_list?.length > 0 ? (
        notes.summaries_list.map((summary, index) => (
          <div key={index} className="mb-4">
            <div className="flex items-start gap-4">
              <span className="text-gray-600 font-semibold text-lg mt-0.5" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>{index + 1}.</span>
              <p className="text-gray-800 leading-relaxed text-base flex-1" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>{summary}</p>
            </div>
          </div>
        ))
      ) : (
        <div className="text-center py-8">
          <List className="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500 text-sm" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>No summaries available yet.</p>
        </div>
      )}
    </div>
  );

  const renderOwnNotes = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="bg-gray-100 text-gray-600 rounded-full p-2">
            <User className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>My Notes</h2>
            <span className="text-gray-500 text-sm" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>Personal thoughts and insights</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          {saving && (
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-gray-500"></div>
              Saving...
            </div>
          )}
          
          {lastSaved && (
            <div className="flex items-center gap-2 text-xs text-green-600">
              <CheckCircle className="h-3 w-3" />
              Saved {lastSaved.toLocaleTimeString()}
            </div>
          )}
          
          <button
            onClick={() => saveOwnNotes()}
            className="flex items-center gap-2 bg-gray-900 text-white px-3 py-1.5 rounded-lg hover:bg-gray-800 transition-colors duration-200 text-xs font-medium"
          >
            <Save className="h-3 w-3" />
            Save
          </button>
        </div>
      </div>
      
      <textarea
        value={ownNotes}
        onChange={handleOwnNotesChange}
        placeholder="Write your personal notes, insights, and thoughts here..."
        className="w-full h-80 p-0 border-0 resize-none focus:ring-0 focus:outline-none text-gray-800 leading-relaxed text-base bg-transparent"
        style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}
      />
      
      <div className="text-xs text-gray-500 mt-2" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>
        💡 Tip: Your notes are automatically saved as you type
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>Loading study notes...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 mb-4 text-lg" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>{error}</div>
          <button
            onClick={loadNotes}
            className="bg-gray-900 text-white px-6 py-3 rounded-lg hover:bg-gray-800 transition-colors duration-200"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'golden', name: 'Golden Notes' },
    { id: 'summaries', name: 'Summaries' },
    { id: 'own', name: 'Own Notes' },
  ];

  return (
    <div className="min-h-screen bg-gray-50" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="w-full px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <button
                onClick={() => navigate(-1)}
                className="text-gray-600 hover:text-gray-900 text-lg font-medium transition-colors"
              >
                ← Back
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Study Notes
                </h1>
                <p className="text-gray-500 text-lg">
                  {notes?.lesson?.title || 'Loading...'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <button
                onClick={regenerateNotes}
                disabled={regenerating}
                className="flex items-center gap-2 bg-gray-900 text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors duration-200 text-sm font-medium disabled:opacity-50"
              >
                <RefreshCw className={`h-4 w-4 ${regenerating ? 'animate-spin' : ''}`} />
                {regenerating ? 'Regenerating...' : 'Regenerate'}
              </button>
              
              <button
                onClick={exportToPDF}
                className="flex items-center gap-2 bg-gray-900 text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors duration-200 text-sm font-medium"
              >
                <Download className="h-4 w-4" />
                Download PDF
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content - Alice.tech Style */}
      <div className="w-full px-6 py-6">
        {/* A4 Paper Container */}
        <div className="bg-white shadow-lg border border-gray-300 mx-auto" style={{
          width: '100%',
          height: 'calc(100vh - 200px)',
          overflow: 'hidden',
          background: '#ffffff',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          border: '1px solid #e5e7eb',
          position: 'relative',
          padding: '40px 60px'
        }}>
          {/* Title */}
          <div className="mb-6">
            <h2 className="text-lg text-gray-600 mb-4" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>
              {notes?.lesson?.title || 'lecture_1.pdf'}
            </h2>
          </div>

          {/* Tab Navigation */}
          <div className="mb-8">
            <nav className="flex border-b border-gray-200">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-3 px-6 text-sm font-medium transition-colors duration-200 ${
                    activeTab === tab.id
                      ? 'text-gray-900 border-b-2 border-gray-900'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                  style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}
                >
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>

          {/* Content - All within frame */}
          <div className="h-full overflow-y-auto">
            {activeTab === 'golden' && renderGoldenNotes()}
            {activeTab === 'summaries' && renderSummaries()}
            {activeTab === 'own' && renderOwnNotes()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudyNotes; 