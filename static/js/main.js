document.addEventListener('DOMContentLoaded', function () {

    // -------------------------------------------------------------
    // 1. FLASHCARD 3D FLIP PLAYER WITH BOOKMARK SYNCHRONIZATION
    // -------------------------------------------------------------
    const flashcardElement = document.getElementById('flashcard-card');
    const prevBtn = document.getElementById('card-prev-btn');
    const nextBtn = document.getElementById('card-next-btn');
    const flipBtn = document.getElementById('card-flip-btn');
    const cardQuestionText = document.getElementById('card-question-text');
    const cardAnswerText = document.getElementById('card-answer-text');
    const cardCounter = document.getElementById('card-counter');
    const cardBookmarkBtn = document.getElementById('card-bookmark-btn');
    const cardCornerBookmark = document.getElementById('card-corner-bookmark');

    if (flashcardElement && window.FLASHCARD_DATA && window.FLASHCARD_DATA.length > 0) {
        let currentIndex = 0;
        const totalCards = window.FLASHCARD_DATA.length;

        function updateCardDisplay() {
            const currentCard = window.FLASHCARD_DATA[currentIndex];

            flashcardElement.classList.remove('flipped');

            setTimeout(() => {
                if (currentCard) {
                    if (cardQuestionText) cardQuestionText.textContent = currentCard.question;
                    if (cardAnswerText) cardAnswerText.textContent = currentCard.answer;
                    if (cardCounter) {
                        cardCounter.textContent = `Card ${currentIndex + 1} of ${totalCards}`;
                    }

                    // Dynamically update card toolbar bookmark button
                    if (cardBookmarkBtn) {
                        cardBookmarkBtn.setAttribute('data-id', currentCard.id);
                        if (currentCard.is_bookmarked) {
                            cardBookmarkBtn.className = 'btn btn-warning px-4 py-2 fw-semibold bookmark-toggle-btn';
                            cardBookmarkBtn.innerHTML = '<i class="bi bi-bookmark-fill me-1"></i> Bookmarked';
                        } else {
                            cardBookmarkBtn.className = 'btn btn-outline-warning px-4 py-2 fw-semibold bookmark-toggle-btn';
                            cardBookmarkBtn.innerHTML = '<i class="bi bi-bookmark me-1"></i> Bookmark Card';
                        }
                    }

                    // Dynamically update corner star bookmark button
                    if (cardCornerBookmark) {
                        cardCornerBookmark.setAttribute('data-id', currentCard.id);
                        if (currentCard.is_bookmarked) {
                            cardCornerBookmark.className = 'card-bookmark-corner bookmark-toggle-btn active is-bookmarked';
                            cardCornerBookmark.innerHTML = '<i class="bi bi-star-fill"></i>';
                            cardCornerBookmark.title = 'Remove bookmark';
                        } else {
                            cardCornerBookmark.className = 'card-bookmark-corner bookmark-toggle-btn';
                            cardCornerBookmark.innerHTML = '<i class="bi bi-star"></i>';
                            cardCornerBookmark.title = 'Bookmark flashcard';
                        }
                    }
                }
            }, 150);

            if (prevBtn) prevBtn.disabled = (currentIndex === 0);
            if (nextBtn) nextBtn.disabled = (currentIndex === totalCards - 1);
        }

        function toggleFlip() {
            flashcardElement.classList.toggle('flipped');
        }

        flashcardElement.addEventListener('click', toggleFlip);
        if (flipBtn) flipBtn.addEventListener('click', toggleFlip);

        if (prevBtn) {
            prevBtn.addEventListener('click', function () {
                if (currentIndex > 0) {
                    currentIndex--;
                    updateCardDisplay();
                }
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', function () {
                if (currentIndex < totalCards - 1) {
                    currentIndex++;
                    updateCardDisplay();
                }
            });
        }

        updateCardDisplay();

        const flashcardTabBtn = document.getElementById('flashcard-tab');
        if (flashcardTabBtn) {
            flashcardTabBtn.addEventListener('shown.bs.tab', function () {
                updateCardDisplay();
            });
        }
    }

    // -------------------------------------------------------------
    // 2. QUIZ TIMER & AUTO-SUBMIT
    // -------------------------------------------------------------
    const quizTimerElement = document.getElementById('quiz-timer');
    const quizForm = document.getElementById('quiz-form');

    if (quizTimerElement && quizForm) {
        let totalMinutes = parseInt(quizTimerElement.getAttribute('data-minutes') || '10');
        let timeRemaining = totalMinutes * 60;

        const timerInterval = setInterval(function () {
            let minutes = Math.floor(timeRemaining / 60);
            let seconds = timeRemaining % 60;

            minutes = minutes < 10 ? '0' + minutes : minutes;
            seconds = seconds < 10 ? '0' + seconds : seconds;

            quizTimerElement.textContent = `${minutes}:${seconds}`;

            if (timeRemaining <= 0) {
                clearInterval(timerInterval);
                alert("Time is up! Submitting your quiz now.");
                quizForm.submit();
            }
            timeRemaining--;
        }, 1000);
    }

    // -------------------------------------------------------------
    // 3. GLOBAL AJAX BOOKMARK SYSTEM (Materials, Subjects, Flashcards, Questions)
    // -------------------------------------------------------------
    document.addEventListener('click', function (e) {
        const btn = e.target.closest('.bookmark-toggle-btn');
        if (!btn) return;

        e.preventDefault();
        const itemType = btn.getAttribute('data-type');
        const itemId = btn.getAttribute('data-id');
        if (!itemType || !itemId) return;

        const csrfToken = getCookie('csrftoken');
        const formData = new FormData();
        formData.append('item_type', itemType);
        formData.append('item_id', itemId);

        btn.style.opacity = '0.7';

        fetch('/bookmark/toggle/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                btn.style.opacity = '1';
                if (data.status === 'added' || data.status === 'removed') {
                    const isAdded = (data.status === 'added');

                    // Synchronize all buttons on current page representing this item
                    const matchingBtns = document.querySelectorAll(`.bookmark-toggle-btn[data-type="${itemType}"][data-id="${itemId}"]`);
                    matchingBtns.forEach(b => {
                        const isCorner = b.classList.contains('card-bookmark-corner');
                        if (isCorner) {
                            if (isAdded) {
                                b.classList.add('active', 'is-bookmarked');
                                b.innerHTML = '<i class="bi bi-star-fill"></i>';
                                b.title = 'Bookmarked';
                            } else {
                                b.classList.remove('active', 'is-bookmarked');
                                b.innerHTML = '<i class="bi bi-star"></i>';
                                b.title = 'Bookmark';
                            }
                        } else {
                            if (isAdded) {
                                b.classList.remove('btn-outline-warning', 'btn-outline-secondary', 'btn-outline-primary', 'btn-outline-light');
                                b.classList.add('btn-warning');
                                const customLabel = b.getAttribute('data-label-active') || 'Bookmarked';
                                b.innerHTML = `<i class="bi bi-bookmark-fill me-1"></i> ${customLabel}`;
                            } else {
                                b.classList.remove('btn-warning');
                                const defaultOutline = b.getAttribute('data-outline-class') || 'btn-outline-warning';
                                b.classList.add(defaultOutline);
                                const customLabel = b.getAttribute('data-label-inactive') || 'Bookmark';
                                b.innerHTML = `<i class="bi bi-bookmark me-1"></i> ${customLabel}`;
                            }
                        }
                    });

                    // Keep in-memory flashcard array synchronized
                    if (itemType === 'flashcard' && window.FLASHCARD_DATA) {
                        const targetCard = window.FLASHCARD_DATA.find(c => String(c.id) === String(itemId));
                        if (targetCard) {
                            targetCard.is_bookmarked = isAdded;
                        }
                    }

                    // If user is removing from Bookmarks page, animate and update counters
                    if (!isAdded) {
                        const bookmarkCard = document.querySelector(`.bookmark-item-card[data-item-type="${itemType}"][data-item-id="${itemId}"]`);
                        if (bookmarkCard) {
                            bookmarkCard.classList.add('removing');
                            setTimeout(() => {
                                bookmarkCard.remove();
                                updateBookmarkCounters();
                            }, 250);
                        }
                    }
                }
            })
            .catch(err => {
                btn.style.opacity = '1';
                console.error('Error toggling bookmark:', err);
            });
    });

    // Helper: live updates for category counters on bookmarks.html
    function updateBookmarkCounters() {
        const remainingCards = document.querySelectorAll('.bookmark-item-card');
        const totalCount = remainingCards.length;

        const totalBadge = document.getElementById('count-all');
        if (totalBadge) totalBadge.textContent = totalCount;

        ['subject', 'material', 'flashcard', 'question'].forEach(cat => {
            const count = document.querySelectorAll(`.bookmark-item-card[data-category="${cat}"]`).length;
            const badge = document.getElementById(`count-${cat}`);
            if (badge) badge.textContent = count;
        });

        const emptyState = document.getElementById('bookmarks-empty-state');
        if (emptyState && totalCount === 0) {
            emptyState.classList.remove('d-none');
        }
    }

    // Filter Tabs on Bookmarks Page
    const filterButtons = document.querySelectorAll('.bookmark-filter-btn');
    if (filterButtons.length > 0) {
        filterButtons.forEach(btn => {
            btn.addEventListener('click', function () {
                filterButtons.forEach(b => b.classList.remove('active'));
                this.classList.add('active');

                const filter = this.getAttribute('data-filter');
                const cards = document.querySelectorAll('.bookmark-item-card');
                let visibleCount = 0;

                cards.forEach(card => {
                    const category = card.getAttribute('data-category');
                    if (filter === 'all' || category === filter) {
                        card.style.display = '';
                        visibleCount++;
                    } else {
                        card.style.display = 'none';
                    }
                });

                const noMatchState = document.getElementById('bookmarks-no-match');
                if (noMatchState) {
                    noMatchState.classList.toggle('d-none', visibleCount > 0);
                }
            });
        });
    }

    // -------------------------------------------------------------
    // 4. MISTAKE REVISION MASTERING
    // -------------------------------------------------------------
    const masterButtons = document.querySelectorAll('.mark-mastered-btn');
    masterButtons.forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const revisionId = this.getAttribute('data-revision-id');
            const csrfToken = getCookie('csrftoken');

            fetch(`/revision/${revisionId}/master/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        window.location.reload();
                    }
                })
                .catch(err => console.error('Error updating revision:', err));
        });
    });

    // -------------------------------------------------------------
    // 5. CSRF COOKIE HELPER
    // -------------------------------------------------------------
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

