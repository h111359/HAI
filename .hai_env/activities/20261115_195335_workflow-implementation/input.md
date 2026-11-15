I want to explore the idea along with the agents the framework to have another functionality - workflows. A workflow should define a process, set of steps which one or several agents should perform in coordination and dependency from each other. I am not sure if this idea is good and how to realize it, so I need your advise, I need you to check the best practices. Make independent recomendation from user perspective, HAI integrity perspective, future scalability perspective, maintainability perspective. Research if similar products have such or close to this functionality and how this is realized there. Be critical. 


User clarification, 2026-11-12 (verbatim):

The workflows should clearly specify the expected input and outputs with their naming standards and locations. Each step should be an instruction to an agent what to do. There should be ability what to happen in case of success or failure of the step. And the workflow should be stored in one or more files with predefined structure. Workflows should be executed in the boundaries of a single activity - no cross-activity workflows. But one activity can have several workflows executed in them. The workflow metadata and status data should be stored in the .hai_env/ folder subfolder - like the files related to agents.


2026-11-14 user authorized preparation of a design-only review package for workflows, accepting the proposed requirements/specification/examples/manager-design/implementation-plan deliverables. Implementation approval is withheld pending review. This entry summarizes scope; it is not a verbatim quotation.


2026-11-15 user instruction (verbatim):
OK, now implement the workflow agents and the whole design


User storage revision (verbatim):
Refactor so the workflow runs to be a subfolder to the current activity. In that way there is no need to have additional level with /<activity-id>/ in it
