const API_BASE = '/api';

/**
 * Fetches all onboarding joiners (new hires) from the backend.
 * @returns {Promise<Array>} A promise resolving to the list of joiners.
 */
export async function fetchJoiners() {
  const res = await fetch(`${API_BASE}/joiners`);
  if (!res.ok) throw new Error('Failed to fetch joiners');
  return res.json();
}

/**
 * Fetches a single joiner's details by their user ID.
 * @param {string} userId - The unique identifier of the joiner.
 * @returns {Promise<Object>} A promise resolving to the joiner details.
 */
export async function fetchJoiner(userId) {
  const res = await fetch(`${API_BASE}/joiners/${userId}`);
  if (!res.ok) throw new Error('Failed to fetch joiner');
  return res.json();
}

/**
 * Submits a new joiner's details to trigger onboarding plan generation.
 * @param {Object} data - Joiner's profiling data (name, role, team, department, BU, start_date).
 * @returns {Promise<Object>} A promise resolving to the created joiner object.
 */
export async function createJoiner(data) {
  const res = await fetch(`${API_BASE}/joiners`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create joiner');
  return res.json();
}

/**
 * Permanently deletes a joiner and their associated plan and tasks.
 * @param {string} userId - The unique identifier of the joiner.
 * @returns {Promise<Object>} A promise resolving to the API response.
 */
export async function deleteJoiner(userId) {
  const res = await fetch(`${API_BASE}/joiners/${userId}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete joiner');
  return res.json();
}

/**
 * Fetches the onboarding plan (including phases and tasks) for a user.
 * @param {string} userId - The unique identifier of the user.
 * @returns {Promise<Object>} A promise resolving to the onboarding plan details.
 */
export async function fetchUserPlan(userId) {
  const res = await fetch(`${API_BASE}/plans/user/${userId}`);
  if (!res.ok) throw new Error('Failed to fetch onboarding plan');
  return res.json();
}

/**
 * Requests an AI plan generation preview without saving it to the database.
 * @param {Object} joinerData - Joiner's profile details.
 * @returns {Promise<Object>} A promise resolving to the generated tasks roadmap.
 */
export async function previewPlan(joinerData) {
  const res = await fetch(`${API_BASE}/plans/preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(joinerData),
  });
  if (!res.ok) throw new Error('Failed to generate plan preview');
  return res.json();
}

/**
 * Updates an existing onboarding plan's tasks or configuration.
 * @param {string} planId - The unique identifier of the onboarding plan.
 * @param {Object} data - The updated tasks list.
 * @returns {Promise<Object>} A promise resolving to the updated plan.
 */
export async function updatePlan(planId, data) {
  const res = await fetch(`${API_BASE}/plans/${planId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to update plan');
  return res.json();
}

/**
 * Fetches dashboard aggregation statistics (joiners count, task completion rates).
 * @returns {Promise<Object>} A promise resolving to the statistics.
 */
export async function fetchDashboardStats() {
  const res = await fetch(`${API_BASE}/plans/dashboard/stats`);
  if (!res.ok) throw new Error('Failed to fetch dashboard stats');
  return res.json();
}

/**
 * Toggles the completion state of a specific onboarding task.
 * @param {string} taskId - The unique identifier of the task.
 * @param {boolean} isCompleted - The new completion status.
 * @returns {Promise<Object>} A promise resolving to the updated task details.
 */
export async function toggleTaskCompletion(taskId, isCompleted) {
  const res = await fetch(`${API_BASE}/tasks/${taskId}/toggle`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ is_completed: isCompleted }),
  });
  if (!res.ok) throw new Error('Failed to toggle task');
  return res.json();
}

/**
 * Sends a chat query to the grounded AI chatbot.
 * @param {string} query - The question asked by the user.
 * @param {string|null} userId - The optional user ID to provide role context.
 * @returns {Promise<Object>} A promise resolving to the chatbot response (answer, citations).
 */
export async function sendChatMessage(query, userId = null) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, user_id: userId }),
  });
  if (!res.ok) throw new Error('Failed to send chat message');
  return res.json();
}

/**
 * Fetches the message history of chat queries for a specific user.
 * @param {string} userId - The unique identifier of the user.
 * @returns {Promise<Array>} A promise resolving to the chat messages history.
 */
export async function fetchChatHistory(userId) {
  const res = await fetch(`${API_BASE}/chat/history/${userId}`);
  if (!res.ok) throw new Error('Failed to fetch chat history');
  return res.json();
}

/**
 * Fetches structural information about the organization (BUs, departments, teams, roles).
 * @returns {Promise<Object>} A promise resolving to the organization chart metadata.
 */
export async function fetchOrgSummary() {
  const res = await fetch(`${API_BASE}/agents/org-expert/summary`);
  if (!res.ok) throw new Error('Failed to fetch org summary');
  return res.json();
}

/**
 * Triggers a scanning of the knowledge base directory to rebuild organizational graphs.
 * @returns {Promise<Object>} A promise resolving to the scan results.
 */
export async function triggerOrgScan() {
  const res = await fetch(`${API_BASE}/agents/org-expert/scan`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to trigger org scan');
  return res.json();
}

/**
 * Fetches all generated learning plans for different roles.
 * @returns {Promise<Array>} A promise resolving to the list of learning plans.
 */
export async function fetchLearningPlans() {
  const res = await fetch(`${API_BASE}/agents/learning-expert/plans`);
  if (!res.ok) throw new Error('Failed to fetch learning plans');
  return res.json();
}

/**
 * Fetches a specific markdown learning plan for a role.
 * @param {string} roleSlug - The slugified name of the role.
 * @returns {Promise<Object>} A promise resolving to the plan contents.
 */
export async function fetchLearningPlan(roleSlug) {
  const res = await fetch(`${API_BASE}/agents/learning-expert/plans/${roleSlug}`);
  if (!res.ok) throw new Error('Failed to fetch learning plan');
  return res.json();
}

/**
 * Updates a specific markdown learning plan's contents.
 * @param {string} roleSlug - The slugified name of the role.
 * @param {string} markdownContent - The updated markdown content.
 * @returns {Promise<Object>} A promise resolving to the save result.
 */
export async function updateLearningPlan(roleSlug, markdownContent) {
  const res = await fetch(`${API_BASE}/agents/learning-expert/plans/${roleSlug}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ markdown_content: markdownContent }),
  });
  if (!res.ok) throw new Error('Failed to update learning plan');
  return res.json();
}

/**
 * Fetches the filenames of all documents in the knowledge base.
 * @returns {Promise<Array>} A promise resolving to the files list.
 */
export async function fetchKBDocs() {
  const res = await fetch(`${API_BASE}/kb/docs`);
  if (!res.ok) throw new Error('Failed to fetch KB docs');
  return res.json();
}

/**
 * Fetches the markdown content of a specific knowledge base document.
 * @param {string} fileName - The filename of the document.
 * @returns {Promise<Object>} A promise resolving to the document content.
 */
export async function fetchKBDoc(fileName) {
  const res = await fetch(`${API_BASE}/kb/docs/${fileName}`);
  if (!res.ok) throw new Error('Failed to fetch KB doc');
  return res.json();
}

/**
 * Performs a search query against the Knowledge Base indexes.
 * @param {string} q - The search query.
 * @returns {Promise<Array>} A promise resolving to the matching sections/documents.
 */
export async function searchKB(q) {
  const res = await fetch(`${API_BASE}/kb/search?q=${encodeURIComponent(q)}`);
  if (!res.ok) throw new Error('Failed to search KB');
  return res.json();
}

/**
 * Fetches all missing feedback queries that did not receive a grounded answer.
 * @returns {Promise<Array>} A promise resolving to the list of missing queries.
 */
export async function fetchMissingFeedback() {
  const res = await fetch(`${API_BASE}/feedback/missing`);
  if (!res.ok) throw new Error('Failed to fetch missing feedback');
  return res.json();
}

/**
 * Resolves a missing feedback query and attaches resolution notes.
 * @param {string} id - Unique identifier of the feedback entry.
 * @param {string} notes - Resolution and actions taken.
 * @returns {Promise<Object>} A promise resolving to the update confirmation.
 */
export async function resolveFeedback(id, notes) {
  const res = await fetch(`${API_BASE}/feedback/resolve/${id}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resolution_notes: notes }),
  });
  if (!res.ok) throw new Error('Failed to resolve feedback');
  return res.json();
}

/**
 * Permanently deletes a missing feedback query.
 * @param {string} id - Unique identifier of the feedback entry.
 * @returns {Promise<Object>} A promise resolving to the deletion confirmation.
 */
export async function deleteFeedback(id) {
  const res = await fetch(`${API_BASE}/feedback/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete feedback');
  return res.json();
}
