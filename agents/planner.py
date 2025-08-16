class PlanningAgent:
    def create_report_outline(self, research_data, topic):
        """Create an outline for the report"""
        
        # Analyze the research data
        themes = self.identify_themes(research_data)
        
        # Create logical sections
        sections = []
        sections.append("Introduction")
        
        for theme in themes:
            sections.append(f"Analysis of {theme}")
        
        sections.append("Conclusions")
        
        # Decide where to put charts
        chart_placements = self.plan_visualizations(sections, research_data)
        
        return {
            "sections": sections,
            "visualizations": chart_placements
        }

    def identify_themes(self, research_data):
        """
        Mock theme identification:
        - In real life, you might use NLP to extract key topics.
        - Here, we just pick keywords from the research data.
        """
        # Convert all text to lowercase for consistency
        all_text = " ".join(research_data).lower()
        keywords = ["ai", "healthcare", "medical imaging", "ethics", "predictive analytics"]

        themes_found = [kw.title() for kw in keywords if kw in all_text]
        if not themes_found:
            themes_found = ["General Insights"]
        return themes_found

    def plan_visualizations(self, sections, research_data):
        """
        Mock chart planning:
        - Places a chart in any section that has enough numeric data.
        """
        chart_placements = {}
        for section in sections:
            if "analysis" in section.lower():
                chart_placements[section] = f"{section.replace(' ', '_').lower()}_chart.png"
        return chart_placements


# # -------------------------
# # Example: Running the agent
# # -------------------------
# if __name__ == "__main__":
#     # Fake research data from our ResearchAgent
#     research_data = [
#         "AI in healthcare is transforming diagnostics",
#         "Medical imaging techniques now use deep learning",
#         "Ethics and regulations in AI adoption are critical",
#         "Predictive analytics helps in early disease detection"
#     ]
    
#     topic = "AI in Healthcare"
#     agent = PlanningAgent()
#     outline = agent.create_report_outline(research_data, topic)

#     print("\n--- Report Outline ---")
#     for sec in outline["sections"]:
#         print(sec)
    
#     print("\n--- Chart Placements ---")
#     for sec, chart in outline["visualizations"].items():
#         print(f"{sec} → {chart}")
