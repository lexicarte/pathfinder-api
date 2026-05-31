REPORT_SCHEMA = {
    "name": "pathfinder_report",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "clientSnapshot": {"type": "string"},
            "strengthsAndPatterns": {
                "type": "array",
                "items": {"type": "string"},
            },
            "transferableSkills": {
                "type": "array",
                "items": {"type": "string"},
            },
            "careerRecommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "title": {"type": "string"},
                        "fitSummary": {"type": "string"},
                        "whyItFits": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "bridgeRoles": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "skillsToBuild": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "possibleJobTitles": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "transitionDifficulty": {"type": "string"},
                    },
                    "required": [
                        "title",
                        "fitSummary",
                        "whyItFits",
                        "bridgeRoles",
                        "skillsToBuild",
                        "possibleJobTitles",
                        "transitionDifficulty",
                    ],
                },
            },
            "resumePositioningKeywords": {
                "type": "array",
                "items": {"type": "string"},
            },
            "watchOuts": {
                "type": "array",
                "items": {"type": "string"},
            },
            "followUpQuestions": {
                "type": "array",
                "items": {"type": "string"},
            },
            "recommendedNextSteps": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        "required": [
            "clientSnapshot",
            "strengthsAndPatterns",
            "transferableSkills",
            "careerRecommendations",
            "resumePositioningKeywords",
            "watchOuts",
            "followUpQuestions",
            "recommendedNextSteps",
        ],
    },
}
