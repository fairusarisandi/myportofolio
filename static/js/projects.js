(() => {
    const config = document.getElementById('project-config');
    const loadingState = document.getElementById('loading');
    const errorState = document.getElementById('error');
    const emptyState = document.getElementById('empty');
    const gridContainer = document.getElementById('grid');
    const searchForm = document.getElementById('project-search-form');
    const searchInput = document.getElementById('search-input');
    const projectForm = document.getElementById('project-form');
    const projectFormModal = document.getElementById('project-form-modal');
    const projectFormTitle = document.querySelector('[data-project-form-title]');
    const projectFormSubmit = document.querySelector('[data-project-form-submit]');
    const projectAddButton = document.querySelector('[data-project-add-button]');
    const projectCardTemplate = document.getElementById('project-card-template');

    if (!config || !loadingState || !errorState || !emptyState || !gridContainer || !searchForm || !searchInput || !projectCardTemplate) {
        console.error('Project page is missing required elements.');
        return;
    }
            
    const projectEndpoints = {
        list: config.dataset.projectsEndpoint,
        create: config.dataset.createEndpoint,
        update: config.dataset.updateUrlTemplate,
        delete: config.dataset.deleteUrlTemplate,
        star: config.dataset.starUrlTemplate,
    };
    const searchDebounceDelay = 300;
    const projectIdPlaceholder = '00000000-0000-0000-0000-000000000000';
    let projectsAbortController;
    let searchDebounceTimer;

    function displayPageSection({ showLoading = false, showError = false, showEmpty = false, showGrid = false }) {
        loadingState.classList.toggle('hide', !showLoading);
        errorState.classList.toggle('hide', !showError);
        emptyState.classList.toggle('hide', !showEmpty);
        gridContainer.classList.toggle('hide', !showGrid);
    }

    function projectUrl(template, projectId) {
        return template.replace(projectIdPlaceholder, encodeURIComponent(projectId));
    }

    function buildProjectCardElement(item) {
        const project = item.fields;
        const projectId = item.pk;
        const card = projectCardTemplate.content.firstElementChild.cloneNode(true);
        const image = card.querySelector('[data-project-thumbnail]');
        const name = project.name || '';
        const modalId = `delete-project-${projectId}`;
        const modalTitleId = `delete-project-title-${projectId}`;

        image.hidden = !project.thumbnail;
        image.classList.toggle('hide', !project.thumbnail);
        if (project.thumbnail) {
            image.src = project.thumbnail;
            image.alt = `Gambar ${name}`;
        }
        card.querySelector('[data-project-name]').textContent = name;
        card.querySelector('[data-project-description]').textContent = project.description || '';

        const starForm = card.querySelector('[data-project-star-form]');
        const starButton = card.querySelector('[data-project-star-button]');
        starForm.action = projectUrl(projectEndpoints.star, projectId);
        starButton.classList.toggle('is-starred', Boolean(project.is_starred));
        starButton.title = project.star_count > 0
            ? `Dibintangi oleh ${project.starred_by_names || ''}`
            : 'Jadilah yang pertama memberi star';
        card.querySelector('[data-project-star-label]').textContent = project.is_starred ? 'Unstar' : 'Star';
        card.querySelector('[data-project-star-count]').textContent = String(project.star_count ?? 0);

        const editButton = card.querySelector('[data-project-edit-button]');
        if (editButton) {
            editButton.dataset.projectId = projectId;
            editButton.dataset.projectName = name;
            editButton.dataset.projectDescription = project.description || '';
            editButton.dataset.projectThumbnail = project.thumbnail || '';
            editButton.setAttribute('aria-label', `Edit ${name}`);
        }

        const deleteTrigger = card.querySelector('[data-project-delete-trigger]');
        const deleteModal = card.querySelector('[data-project-delete-modal]');
        if (deleteTrigger && deleteModal) {
            deleteModal.id = modalId;
            deleteModal.setAttribute('aria-labelledby', modalTitleId);
            deleteTrigger.setAttribute('popovertarget', modalId);
            deleteTrigger.setAttribute('aria-label', `Hapus ${name}`);
            deleteModal.querySelector('[data-project-delete-title]').id = modalTitleId;
            deleteModal.querySelector('[data-project-delete-name]').textContent = name;
            deleteModal.querySelectorAll('[popovertargetaction="hide"]').forEach((button) => {
                button.setAttribute('popovertarget', modalId);
            });
            deleteModal.querySelector('[data-project-delete-form]').action =
                projectUrl(projectEndpoints.delete, projectId);
        }

        return card;
    }

    async function fetchProjects(searchQuery = '') {
        projectsAbortController?.abort();
        projectsAbortController = new AbortController();

        try {
            displayPageSection({ showLoading: true });
            const url = new URL(projectEndpoints.list, window.location.href);
            if (searchQuery) {
                url.searchParams.set('name', searchQuery);
            }

            const response = await fetch(url, {
                headers: { Accept: 'application/json' },
                signal: projectsAbortController.signal,
            });
            if (!response.ok) {
                throw new Error(`Failed to fetch projects (status ${response.status}).`);
            }

            const projectData = await response.json();
            if (!Array.isArray(projectData)) {
                throw new Error('Project API returned an invalid response.');
            }

            gridContainer.replaceChildren();
            if (projectData.length === 0) {
                displayPageSection({ showEmpty: true });
                return;
            }

            projectData.forEach((item) => {
                gridContainer.appendChild(buildProjectCardElement(item));
            });
            displayPageSection({ showGrid: true });
        } catch (error) {
            if (error.name === 'AbortError') {
                return;
            }
            console.error('Error loading projects:', error);
            displayPageSection({ showError: true });
        }
    }

    function searchProjects() {
        fetchProjects(searchInput.value.trim());
    }

    searchInput.addEventListener('input', () => {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(searchProjects, searchDebounceDelay);
    });

    searchForm.addEventListener('submit', (event) => {
        event.preventDefault();
        clearTimeout(searchDebounceTimer);
        searchProjects();
    });

    let editingProjectId = null;

    function prepareProjectFormForCreate() {
        if (!projectForm) {
            return;
        }
        editingProjectId = null;
        projectForm.reset();
        projectFormTitle.textContent = 'Tambah Proyek Baru';
        projectFormSubmit.textContent = 'Tambah Proyek';
    }

    projectAddButton?.addEventListener('click', prepareProjectFormForCreate);

    gridContainer.addEventListener('click', (event) => {
        const editButton = event.target.closest('[data-project-edit-button]');
        if (!editButton || !projectForm || !projectFormModal) {
            return;
        }

        editingProjectId = editButton.dataset.projectId;
        projectForm.elements.namedItem('name').value = editButton.dataset.projectName;
        projectForm.elements.namedItem('description').value = editButton.dataset.projectDescription;
        projectForm.elements.namedItem('thumbnail').value = editButton.dataset.projectThumbnail;
        projectFormTitle.textContent = 'Edit Proyek';
        projectFormSubmit.textContent = 'Simpan Perubahan';
        projectFormModal.showPopover();
    });

    gridContainer.addEventListener('submit', async (event) => {
        const starForm = event.target.closest('[data-project-star-form]');
        if (!starForm) {
            return;
        }

        event.preventDefault();
        const starButton = starForm.querySelector('[data-project-star-button]');
        starButton.disabled = true;

        try {
            const response = await fetch(starForm.action, {
                method: 'POST',
                headers: {
                    Accept: 'application/json',
                    'X-CSRFToken': starForm.querySelector('[name="csrfmiddlewaretoken"]').value,
                },
            });
            if (!response.headers.get('content-type')?.includes('application/json')) {
                throw new Error(
                    response.redirected
                        ? 'Silakan login untuk memberi star.'
                        : 'Server mengembalikan respons yang tidak valid.',
                );
            }
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.message || `Terjadi kesalahan (status ${response.status}).`);
            }
            if (
                typeof result.is_starred !== 'boolean'
                || !Number.isInteger(result.star_count)
                || typeof result.starred_by_names !== 'string'
            ) {
                throw new Error('Server mengembalikan status star yang tidak valid.');
            }

            starButton.classList.toggle('is-starred', result.is_starred);
            starButton.title = result.star_count > 0
                ? `Dibintangi oleh ${result.starred_by_names}`
                : 'Jadilah yang pertama memberi star';
            starForm.querySelector('[data-project-star-label]').textContent =
                result.is_starred ? 'Unstar' : 'Star';
            starForm.querySelector('[data-project-star-count]').textContent = String(result.star_count);
        } catch (error) {
            console.error('Error toggling project star:', error);
            showToast('Gagal memperbarui star', error.message || 'Tidak dapat terhubung ke server. Silakan coba lagi.', 'error');
        } finally {
            starButton.disabled = false;
        }
    });

    if (projectForm) {
        projectForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const submitButton = projectForm.querySelector('button[type="submit"]');
            if (!submitButton) {
                console.error('Project form is missing its submit button.');
                return;
            }
            submitButton.disabled = true;

            const isEditing = Boolean(editingProjectId);
            const endpoint = isEditing
                ? projectUrl(projectEndpoints.update, editingProjectId)
                : projectEndpoints.create;

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        Accept: 'application/json',
                        'X-CSRFToken': projectForm.querySelector('[name="csrfmiddlewaretoken"]')?.value || '',
                    },
                    body: new FormData(projectForm),
                });
                if (!response.headers.get('content-type')?.includes('application/json')) {
                    throw new Error(
                        response.redirected
                            ? 'Sesi login berakhir. Silakan login kembali.'
                            : 'Server mengembalikan respons yang tidak valid.',
                    );
                }
                const result = await response.json();

                if (response.ok) {
                    projectForm.reset();
                    projectFormModal?.hidePopover();
                    editingProjectId = null;
                    showToast(
                        'Berhasil',
                        isEditing ? 'Proyek berhasil diperbarui!' : 'Proyek baru berhasil ditambahkan!',
                        'success',
                    );
                    fetchProjects(searchInput.value.trim());
                } else {
                    const errorMessages = result.errors
                        ? Object.values(result.errors).flat().map((error) => error.message)
                        : [result.message || `Terjadi kesalahan (status ${response.status}).`];
                    showToast(
                        isEditing ? 'Gagal mengubah proyek' : 'Gagal menambahkan proyek',
                        errorMessages.join(' '),
                        'error',
                    );
                }
            } catch (error) {
                console.error(isEditing ? 'Error updating project:' : 'Error adding project:', error);
                showToast(
                    isEditing ? 'Gagal mengubah proyek' : 'Gagal menambahkan proyek',
                    error.message || 'Tidak dapat terhubung ke server. Silakan coba lagi.',
                    'error',
                );
            } finally {
                submitButton.disabled = false;
            }
        });
    }

    fetchProjects(searchInput.value.trim());
})();
