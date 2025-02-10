document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ 스크립트 로드 완료");
    // 좋아요 버튼 클릭 이벤트
    document.querySelectorAll(".like-btn").forEach(button => {
        button.addEventListener("click", handleLikeClick);
    });

    // ✅ 좋아요 버튼 클릭 시 실행되는 함수
    function handleLikeClick(event) {
        // event.preventDefault();

        const button = event.currentTarget;
        const postId = button.getAttribute("data-post-id");
        const category = button.getAttribute("data-category");

        if (!postId || !category) {
            console.error("🚨 잘못된 좋아요 요청: postId 또는 category 없음");
            return;
        }

        console.log(`❤️ 좋아요 요청: postId=${postId}, category=${category}`);

        // ✅ 중복 클릭 방지
        if (button.disabled) return;
        button.disabled = true;

        fetch(`/like/${category}/${postId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log("✅ 좋아요 요청 결과:", data);
            if (data.success) {
                // ✅ UI 업데이트 (❤️ → 🤍 또는 🤍 → ❤️)
                const likeCount = button.querySelector(".like-count");
                let currentLikes = parseInt(likeCount.textContent) || 0;

                if (data.liked) {
                    button.innerHTML = `❤️ <span class="like-count">${currentLikes + 1}</span>`;
                } else {
                    button.innerHTML = `🤍 <span class="like-count">${currentLikes - 1}</span>`;
                }
            } else {
                throw new Error(data.error || "좋아요 처리 실패");
            }
        })
        .catch(error => {
            console.error("🚨 좋아요 요청 중 오류:", error);
            if (!window.likeErrorShown) {
                window.likeErrorShown = true;
                alert("서버와의 통신 중 오류가 발생했습니다.");
                setTimeout(() => { window.likeErrorShown = false; }, 2000);
            }
        })
        .finally(() => {
            button.disabled = false; // 버튼 활성화
        });
    }

    // ✅ 채팅하기 버튼 이벤트 추가
    document.querySelectorAll(".chat-btn").forEach(function (button) {
        button.addEventListener("click", function (event) {
            // event.preventDefault();

            let postId = this.getAttribute("data-post-id");
            let authorId = this.getAttribute("data-author-id");
            let category = this.getAttribute("data-category");

            if (!postId || !authorId || !category) {
                alert("❌ 필요한 정보가 없습니다.");
                return;
            }

            console.log(`🗨️ 채팅 요청: postId=${postId}, authorId=${authorId}, category=${category}`);

            fetch(`/start_chat/${postId}/${authorId}/${category}`, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ post_id: postId, author_id: authorId, category: category })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = data.chat_url;
                } else {
                    alert(data.error || "채팅을 시작할 수 없습니다.");
                }
            })
            .catch(error => {
                console.error("🚨 Error:", error.message);
                alert("채팅방 생성 중 오류가 발생했습니다.");
            });
        });
    });
    console.log("✅ 스크립트 로드 완료");

    
   
        // ✅ 스크롤 다운 버튼 기능 추가
    // const scrollDownBtn = document.getElementById("scroll-down-btn");

    // if (!document.getElementById("scroll-down-btn")) {
    //     let scrollDownBtn = document.createElement("button");
    //     scrollDownBtn.id = "scroll-down-btn";
    //     scrollDownBtn.classList.add("scroll-down-btn");
    //     scrollDownBtn.innerHTML = "";
    //     document.body.appendChild(scrollDownBtn);

    //     scrollDownBtn.addEventListener("click", function () {
    //         window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
    //     });

    //     window.addEventListener("scroll", function () {
    //         scrollDownBtn.style.display = window.scrollY > 300 ? "block" : "none";
    //     });
    // }
   
    // let scrollDownBtn = document.getElementById("scroll-down-btn");
    // // ✅ 기존에 스크롤 버튼이 없으면 새로 추가
    // if (!scrollDownBtn) {
    //     scrollDownBtn = document.createElement("button");
    //     scrollDownBtn.id = "scroll-down-btn";
    //     scrollDownBtn.classList.add("scroll-down-btn");
    //     scrollDownBtn.innerHTML = "⬇️";
    //     document.body.appendChild(scrollDownBtn);
    // }

    // // ✅ 스크롤 버튼 클릭 시 페이지 맨 아래로 이동
    // scrollDownBtn.addEventListener("click", function () {
    //     window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
    // });

    // // ✅ 페이지 스크롤 이벤트 (일정 높이 이상 내려가면 버튼 보이기)
    // window.addEventListener("scroll", function () {
    //     scrollDownBtn.style.display = window.scrollY > 300 ? "block" : "none";
    // });
    // let footer = document.querySelector(".main-footer");
    // let mainContent = document.querySelector(".main-container");

    // function adjustFooterPosition() {
    //     let windowHeight = window.innerHeight;
    //     let contentHeight = mainContent.offsetHeight + footer.offsetHeight;

    //     if (contentHeight < windowHeight) {
    //         footer.style.position = "absolute";
    //         footer.style.bottom = "0";
    //         footer.style.width = "100%";
    //     } else {
    //         footer.style.position = "relative";
    //     }
    // }

    // adjustFooterPosition();
    // window.addEventListener("resize", adjustFooterPosition);

    // ✅ 반려동물 입력 필드 동적 표시 (회원가입 전용)
    const petRadios = document.querySelectorAll('input[name="has_pet"]');
    if (petRadios.length > 0) {
        petRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                const petInfo = document.getElementById('pet-info');
                const isRequired = this.value === 'yes';

                petInfo.style.display = isRequired ? 'block' : 'none';

                document.getElementById('pet_name').required = isRequired;
                document.getElementById('species').required = isRequired;
                document.getElementById('age').required = isRequired;
                document.getElementById('personality').required = isRequired;

                if (!isRequired) {
                    document.getElementById('pet_name').value = '';
                    document.getElementById('species').value = '';
                    document.getElementById('age').value = '';
                    document.getElementById('personality').value = '';
                }
            });
        });
    }
    // ✅ 세션 데이터 가져오기
    const sessionDataElement = document.getElementById("session-data");

    if (!sessionDataElement) {
        console.warn("⚠️ 세션 데이터 요소를 찾을 수 없습니다.");
        return;
    }

    const userProvince = sessionDataElement.getAttribute("data-province") || "";
    const userCity = sessionDataElement.getAttribute("data-city") || "";
    const userDistrict = sessionDataElement.getAttribute("data-district") || "";

    console.log("✅ 로그인한 사용자의 지역 정보:", userProvince, userCity, userDistrict);

    // ✅ 도/시/동 셀렉트박스 요소 가져오기
    const provinceSelect = document.getElementById("province");
    const citySelect = document.getElementById("city");
    const districtSelect = document.getElementById("district");
    const filterButton = document.getElementById("filterBtn");

    if (!provinceSelect || !citySelect || !districtSelect) {
        console.warn("⚠️ 지역 선택 요소가 HTML에 없습니다.");
        return;
    }

    // ✅ 지역 데이터를 로드하여 도/시/동 셀렉트 박스에 적용
    let regionData;
    fetch("/static/regions.json")
        .then(response => response.json())
        .then(data => {
            regionData = data;
            console.log("✅ 지역 데이터 로드 성공:", regionData);

            if (regionData && Object.keys(regionData).length > 0) {
                console.log("📌 로그인한 사용자의 지역 정보 적용");
                populateProvinces(true, userProvince);
            } else {
                console.error("🚨 지역 데이터가 비어 있음!");
            }
        })
        .catch(error => {
            console.error("🚨 지역 데이터 로드 실패:", error);
        });

    // ✅ 도 목록 채우기 (첫 번째 값 자동 선택)
    function populateProvinces(addAllOption, selectedProvince) {
        console.log("✅ populateProvinces() 실행됨");
        provinceSelect.innerHTML = '';

        if (addAllOption) {
            const defaultOption = document.createElement("option");
            defaultOption.value = "";
            defaultOption.textContent = "전체";
            provinceSelect.appendChild(defaultOption);
        }

        let provinces = Object.keys(regionData);
        provinces.forEach(province => {
            const option = document.createElement("option");
            option.value = province;
            option.textContent = province;
            provinceSelect.appendChild(option);

            if (selectedProvince && province === selectedProvince) {
                option.selected = true;
            }
        });

        provinceSelect.dispatchEvent(new Event("change"));
    }

    // ✅ 도 선택 시 시 목록 자동 채우기
    provinceSelect.addEventListener("change", function () {
        citySelect.innerHTML = "";
        districtSelect.innerHTML = "";

        const selectedProvince = this.value;
        const defaultOption = document.createElement("option");
        defaultOption.value = "";
        defaultOption.textContent = "전체";
        citySelect.appendChild(defaultOption);

        if (selectedProvince && regionData[selectedProvince]) {
            let cities = Object.keys(regionData[selectedProvince]);

            cities.forEach(city => {
                const option = document.createElement("option");
                option.value = city;
                option.textContent = city;
                citySelect.appendChild(option);

                if (city === userCity) {
                    option.selected = true;
                }
            });
        }

        citySelect.dispatchEvent(new Event("change"));
    });

    // ✅ 시 선택 시 동 목록 자동 채우기
    citySelect.addEventListener("change", function () {
        districtSelect.innerHTML = "";
        const selectedProvince = provinceSelect.value;
        const selectedCity = this.value;
        const defaultOption = document.createElement("option");
        defaultOption.value = "";
        defaultOption.textContent = "전체";
        districtSelect.appendChild(defaultOption);

        if (selectedProvince && selectedCity && regionData[selectedProvince][selectedCity]) {
            let districts = regionData[selectedProvince][selectedCity];

            districts.forEach(district => {
                const option = document.createElement("option");
                option.value = district;
                option.textContent = district;
                districtSelect.appendChild(option);

                if (district === userDistrict) {
                    option.selected = true;
                }
            });
        }
    });

    // ✅ 검색 버튼 클릭 시 필터링 실행
    if (filterButton) {
        filterButton.addEventListener("click", function () {
            let selectedProvince = provinceSelect.value.trim();
            let selectedCity = citySelect.value.trim();
            let selectedDistrict = districtSelect.value.trim();

            console.log("🔍 필터링 요청:", selectedProvince, selectedCity, selectedDistrict);

            const queryParams = new URLSearchParams({
                province: selectedProvince,
                city: selectedCity,
                district: selectedDistrict
            }).toString();

            window.location.href = window.location.pathname + "?" + queryParams;
        });
    }
  

    // ✅ 페이지 로드 시 자동 필터링 실행 (산책방/돌봄방 진입 시)
    // const urlParams = new URLSearchParams(window.location.search);
    // const hasFilters = urlParams.has("province") && urlParams.has("city");

    // if (!hasFilters && userProvince && userCity) {
    //     console.log("🚀 자동 필터링 적용 중...");
    //     const queryParams = new URLSearchParams({
    //         province: userProvince,
    //         city: userCity,
    //         district: userDistrict || ""
    //     }).toString();

    //     if (!window.location.search.includes("province")) {
    //         window.location.href = window.location.pathname + "?" + queryParams;
    //     }
    // }
    //산책 게시글 수정
    document.querySelectorAll(".edit-btn").forEach(button => {
        button.addEventListener("click", function () {
            const postId = this.getAttribute("data-post-id");
            const category = this.getAttribute("data-category");
            
            if (!postId || !category) {
                console.error("🚨 수정 요청 실패: postId 또는 category 없음");
                return;
            }
            
            console.log(`✏️ 수정 요청: postId=${postId}, category=${category}`);
            window.location.href = `/walks/edit/${postId}`;
        });
    });
    // });
    // document.querySelector(".btn-outline-primary").addEventListener("click", () => {
    //     console.log("글 작성 버튼이 클릭됨!");
    // });
    // let showForm = urlParams.get("show_form").toLowerCase(); 

    
    // 삭제
    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", function () {
            const postId = this.getAttribute("data-post-id");
            const category = this.getAttribute("data-category");

            if (!postId || !category) {
                alert("❌ 게시글 정보를 가져올 수 없습니다.");
                return
            }

            if (!confirm("정말로 삭제하시겠습니까?")) return;

            fetch(`/delete_post/${category}/${postId}`, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/json"
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("✅ 게시글이 삭제되었습니다.");
                    window.location.reload();
                } else {
                    alert(`❌ 삭제 실패: ${data.message}`);
                }
            })
            .catch(error => {
                console.error("🚨 삭제 요청 오류:", error);
                alert("서버와의 통신 중 오류가 발생했습니다.");
            });
        });
    })
});
