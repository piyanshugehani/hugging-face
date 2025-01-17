import { useState } from 'react';
import './App.css';
import Header from './Header';
import Recommendations from './Recommendations';

function App() {
  const [inputText, setInputText] = useState('');
  const [generatedContent, setGeneratedContent] = useState('');
  const [error, setError] = useState('');
  const [knowledgeInfo, setKnowledgeInfo] = useState(''); // State for displaying knowledge base info

  // Static knowledge base as a JSON object
  const knowledgeBase = {
    "Astronaut": "An astronaut is a person who is trained to travel in space.",
    "Horse": "Horses are large animals that are often used for riding, racing, and other sports.",
    "Space": "Space is the vast, seemingly infinite expanse that exists beyond the Earth's atmosphere."
  };

  // Function to retrieve relevant context from the knowledge base
  const queryKnowledgeBase = (query) => {
    const keywords = Object.keys(knowledgeBase);
    const relevantData = keywords.filter((keyword) => query.includes(keyword));
    
    // If no relevant data found, return a default message
    if (relevantData.length === 0) {
      return "No relevant information found. this is only a hugging face text-to-image. not gemini pro";
    }

    // Combine relevant information
    return relevantData.map((keyword) => knowledgeBase[keyword]).join(' '); 
  };

  // The query function to fetch the data from Hugging Face
  const queryGenerativeModel = async (data) => {
    const response = await fetch(
      "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev",
      {
        headers: {
          Authorization: "Bearer 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",
          "Content-Type": "application/json",
        },
        method: "POST",
        body: JSON.stringify(data),
      }
    );

    if (!response.ok) {
      throw new Error("Failed to fetch the generative model.");
    }

    const result = await response.blob();
    return URL.createObjectURL(result);
  };

  // Handle the button click
  const handleGenerate = async () => {
    setError('');
    try {
      // Step 1: Query the knowledge base
      const knowledgeData = queryKnowledgeBase(inputText);
      setKnowledgeInfo(knowledgeData); // Set the knowledge info state

      // Step 2: Prepare data for generative model
      const combinedData = {
        inputs: `${inputText}\nContext: ${knowledgeData}`, // Combine input text with knowledge
      };

      // Step 3: Query the generative model
      const response = await queryGenerativeModel(combinedData);
      setGeneratedContent(response);
    } catch (error) {
      setError(error.message);
      console.error("Error:", error);
    }
  };

  return (
    <>
      <Header />
      <div className="mt-10 flex flex-col items-center space-y-4">
        <div className="flex">
          <input
            type="text"
            placeholder="Enter text"
            className="border border-gray-300 rounded-l-md p-4 focus:outline-none focus:ring-2 focus:ring-blue-400"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
          />
          <button
            className="bg-gray-900 text-white rounded-r-md p-4"
            onClick={handleGenerate}
          >
            Generate
          </button>
        </div>

        <div className="w-full max-w-md bg-white border border-gray-300 rounded-md p-4 shadow-md">
          {error && <p className="text-red-500">{error}</p>}
          {knowledgeInfo && (
            <div className="mb-4">
              <h2 className="font-bold">Relevant Information:</h2>
              <p>{knowledgeInfo}</p>
            </div>
          )}
          {generatedContent ? (
            <img src={generatedContent} alt="Generated" className="w-full h-auto" />
          ) : (
            <p>Your generated content will appear here.</p>
          )}
        </div>
        <Recommendations/>
      </div>
    </>
  );
}

export default App;
