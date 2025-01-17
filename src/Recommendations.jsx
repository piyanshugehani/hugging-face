import React, { useState } from "react";

const Recommendations = () => {
  const [preferences, setPreferences] = useState([]);
  const [recommendations, setRecommendations] = useState([]);

  const fetchRecommendations = async () => {
    try {
      console.log("Preferences Sent:", preferences);

      const response = await fetch("http://127.0.0.1:5000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ preferences }),
      });
      

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      console.log("Response Data:", data);

      setRecommendations(data.recommendations);
    } catch (error) {
      console.error("Fetch error:", error);
    }
  };

  return (
    <div>
      <h1>Recommendation System</h1>
      <input
        type="text"
        placeholder="Enter preferences (comma-separated)"
        onChange={(e) =>
          setPreferences(e.target.value.split(",").map((pref) => pref.trim()))
        }
      />
      <button
        className="bg-yellow-500 text-white px-4 py-2 rounded"
        onClick={fetchRecommendations}
      >
        Get Recommendations
      </button>
      <ul>
        {recommendations.map((item) => (
          <li key={item.id}>{item.name}</li>
        ))}
      </ul>
    </div>
  );
};

export default Recommendations;
