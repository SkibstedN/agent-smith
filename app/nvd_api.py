import requests
import json
from typing import Dict, List, Optional
import time
import os

class NVDApi:
    def __init__(self):
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.api_key = os.getenv("NVD_API_KEY", "")
        self.headers = {
            "Accept": "application/json",
            "apiKey": self.api_key
        }
        # Rate limiting: NVD allows 5 requests per 30 seconds without API key
        # With API key: 50 requests per 30 seconds
        self.rate_limit = 50 if self.api_key else 5
        self.rate_limit_window = 30
        self.last_request_time = 0
        self.request_count = 0

    def _handle_rate_limit(self):
        """Handle NVD API rate limiting"""
        current_time = time.time()
        if current_time - self.last_request_time >= self.rate_limit_window:
            self.request_count = 0
            self.last_request_time = current_time
        elif self.request_count >= self.rate_limit:
            sleep_time = self.rate_limit_window - (current_time - self.last_request_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
            self.request_count = 0
            self.last_request_time = time.time()
        self.request_count += 1

    def search_cves(self, keyword: str, start_index: int = 0, results_per_page: int = 20) -> Dict:
        """Search for CVEs using keywords"""
        try:
            self._handle_rate_limit()
            # Format the keyword for better search results
            formatted_keyword = f"{keyword} version"
            params = {
                "keywordSearch": formatted_keyword,
                "startIndex": start_index,
                "resultsPerPage": results_per_page,
                "pubStartDate": "2014-01-01T00:00:00.000"  # Limit to recent CVEs
            }
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # If no results, try a broader search
            if data.get("totalResults", 0) == 0:
                params["keywordSearch"] = keyword.split()[0]  # Just use the first word
                response = requests.get(self.base_url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            return data
        except requests.exceptions.RequestException as e:
            print(f"Warning: Error searching CVEs for {keyword}: {str(e)}")
            return {"totalResults": 0, "vulnerabilities": []}

    def get_cve_details(self, cve_id: str) -> Optional[Dict]:
        """Get detailed information about a specific CVE"""
        try:
            self._handle_rate_limit()
            params = {
                "cveId": cve_id
            }
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("totalResults", 0) > 0:
                return data["vulnerabilities"][0]
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error getting CVE details: {str(e)}")
            return None

    def get_cves_by_cpe(self, cpe_name: str) -> List[Dict]:
        """Get CVEs associated with a specific CPE"""
        try:
            self._handle_rate_limit()
            params = {
                "cpeName": cpe_name
            }
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("vulnerabilities", [])
        except requests.exceptions.RequestException as e:
            print(f"Error getting CVEs by CPE: {str(e)}")
            return []

    def format_vulnerability_report(self, cve_data: Dict) -> Dict:
        """Format CVE data into a structured report"""
        if not cve_data:
            return {}

        cve = cve_data.get("cve", {})
        metrics = cve.get("metrics", {})
        cvss_data = metrics.get("cvssMetricV31", [{}])[0] if metrics.get("cvssMetricV31") else {}

        # Generate testing steps based on CVE type
        testing_steps = self._generate_testing_steps(cve_data)

        return {
            "cve_id": cve.get("id"),
            "description": cve.get("descriptions", [{}])[0].get("value", "No description available"),
            "cvss_score": cvss_data.get("cvssData", {}).get("baseScore"),
            "severity": cvss_data.get("cvssData", {}).get("baseSeverity"),
            "references": [ref.get("url") for ref in cve.get("references", [])],
            "cwe": [weakness.get("description", [{}])[0].get("value") 
                   for weakness in cve.get("weaknesses", [])],
            "is_exploited": cve.get("cisaExploitAdd", False),
            "recommendations": self._generate_recommendations(cve_data),
            "testing_steps": testing_steps
        }

    def _generate_testing_steps(self, cve_data: Dict) -> List[str]:
        """Generate specific testing steps based on CVE type"""
        steps = []
        cve = cve_data.get("cve", {})
        description = cve.get("descriptions", [{}])[0].get("value", "").lower()
        
        # Add steps based on vulnerability type
        if "sql injection" in description:
            steps.extend([
                "Test all user input fields for SQL injection",
                "Use automated SQL injection tools (e.g., SQLmap)",
                "Check for error messages that reveal database information"
            ])
        elif "xss" in description or "cross-site scripting" in description:
            steps.extend([
                "Test all user input fields for XSS",
                "Check for proper output encoding",
                "Test both reflected and stored XSS vectors"
            ])
        elif "buffer overflow" in description:
            steps.extend([
                "Identify the vulnerable component",
                "Test with various input lengths",
                "Check for crash conditions"
            ])
        elif "denial of service" in description or "dos" in description:
            steps.extend([
                "Test resource exhaustion scenarios",
                "Monitor system resources during testing",
                "Check for proper rate limiting"
            ])
        
        # Add general steps
        steps.extend([
            "Verify the vulnerability exists in your environment",
            "Document the steps to reproduce",
            "Test any available patches or workarounds"
        ])
        
        return steps

    def _generate_recommendations(self, cve_data: Dict) -> List[str]:
        """Generate recommendations based on CVE data"""
        recommendations = []
        cve = cve_data.get("cve", {})
        
        # Add vendor advisories
        for ref in cve.get("references", []):
            if ref.get("tags", []):
                recommendations.append(f"Check vendor advisory: {ref.get('url')}")

        # Add general recommendations based on severity
        metrics = cve.get("metrics", {})
        cvss_data = metrics.get("cvssMetricV31", [{}])[0] if metrics.get("cvssMetricV31") else {}
        severity = cvss_data.get("cvssData", {}).get("baseSeverity", "").lower()

        if severity == "critical":
            recommendations.append("Immediate action required. Patch or mitigate as soon as possible.")
        elif severity == "high":
            recommendations.append("High priority. Schedule patching within 24-48 hours.")
        elif severity == "medium":
            recommendations.append("Medium priority. Plan patching within the next week.")
        elif severity == "low":
            recommendations.append("Low priority. Include in regular maintenance cycle.")

        return recommendations 