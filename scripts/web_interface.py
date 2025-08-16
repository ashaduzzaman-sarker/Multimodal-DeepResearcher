<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multimodal DeepResearcher</title>
    <script src="https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@babel/standalone@7.22.9/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        const { useState, useEffect } = React;

        function App() {
            const [topic, setTopic] = useState('');
            const [description, setDescription] = useState('');
            const [style, setStyle] = useState('academic');
            const [status, setStatus] = useState(null);
            const [progress, setProgress] = useState(0);
            const [taskId, setTaskId] = useState(null);
            const [isGenerating, setIsGenerating] = useState(false);

            const handleSubmit = async (e) => {
                e.preventDefault();
                setIsGenerating(true);
                setStatus(null);
                setProgress(10);

                try {
                    const response = await fetch('/generate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ topic, description, style })
                    });
                    const result = await response.json();

                    if (result.success) {
                        setTaskId(result.task_id);
                        pollStatus(result.task_id);
                    } else {
                        setStatus({ type: 'error', message: result.error });
                        setIsGenerating(false);
                        setProgress(0);
                    }
                } catch (error) {
                    setStatus({ type: 'error', message: error.message });
                    setIsGenerating(false);
                    setProgress(0);
                }
            };

            const pollStatus = async (taskId) => {
                const interval = setInterval(async () => {
                    try {
                        const response = await fetch(`/status/${taskId}`);
                        const data = await response.json();
                        setProgress(data.progress);
                        
                        if (data.status === 'completed') {
                            clearInterval(interval);
                            setStatus({
                                type: 'success',
                                message: (
                                    <>
                                        <strong>Report Generated Successfully!</strong><br />
                                        <a href={`/download/${taskId}`} target="_blank" className="text-blue-600 hover:underline">Download Report</a> | 
                                        <a href={`/view/${taskId}`} target="_blank" className="text-blue-600 hover:underline">View Online</a>
                                    </>
                                )
                            });
                            setIsGenerating(false);
                        } else if (data.status === 'failed') {
                            clearInterval(interval);
                            setStatus({ type: 'error', message: data.error });
                            setIsGenerating(false);
                            setProgress(0);
                        }
                    } catch (error) {
                        console.error('Polling error:', error);
                    }
                }, 2000);
            };

            return (
                <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center p-4">
                    <div className="bg-white rounded-xl shadow-2xl p-8 max-w-2xl w-full">
                        <h1 className="text-3xl font-bold text-gray-800 mb-2 text-center">🤖 Multimodal DeepResearcher</h1>
                        <p className="text-gray-600 text-center mb-6">Generate professional research reports with AI-powered analysis and interactive visualizations</p>
                        
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div>
                                <label htmlFor="topic" className="block text-sm font-medium text-gray-700">Research Topic *</label>
                                <input
                                    type="text"
                                    id="topic"
                                    value={topic}
                                    onChange={(e) => setTopic(e.target.value)}
                                    required
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                    placeholder="e.g., 'Impact of AI on Healthcare'"
                                />
                            </div>
                            <div>
                                <label htmlFor="description" className="block text-sm font-medium text-gray-700">Additional Context (Optional)</label>
                                <textarea
                                    id="description"
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                    placeholder="Specific aspects to focus on..."
                                    rows={4}
                                />
                            </div>
                            <div>
                                <label htmlFor="style" className="block text-sm font-medium text-gray-700">Report Style</label>
                                <select
                                    id="style"
                                    value={style}
                                    onChange={(e) => setStyle(e.target.value)}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                                >
                                    <option value="academic">Academic</option>
                                    <option value="business">Business</option>
                                    <option value="casual">General Audience</option>
                                </select>
                            </div>
                            <button
                                type="submit"
                                disabled={isGenerating}
                                className={`w-full py-3 px-4 rounded-md text-white font-semibold ${isGenerating ? 'bg-gray-400 cursor-not-allowed' : 'bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700'} transition-transform duration-200 ${isGenerating ? '' : 'hover:-translate-y-1'}`}
                            >
                                {isGenerating ? '🔄 Generating...' : '🚀 Generate Report'}
                            </button>
                        </form>
                        
                        {progress > 0 && (
                            <div className="mt-6">
                                <div className="w-full bg-gray-200 rounded-full h-4">
                                    <div
                                        className="bg-gradient-to-r from-indigo-500 to-purple-600 h-4 rounded-full transition-all duration-300"
                                        style={{ width: `${progress}%` }}
                                    ></div>
                                </div>
                            </div>
                        )}
                        
                        {status && (
                            <div className={`mt-4 p-4 rounded-md ${status.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                {status.message}
                            </div>
                        )}
                    </div>
                </div>
            );
        }

        ReactDOM.render(<App />, document.getElementById('root'));
    </script>
</body>
</html>