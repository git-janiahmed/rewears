document.addEventListener('DOMContentLoaded', function () {
  const mainMenuItems = document.querySelectorAll('.main-item');
  const subcategoriesDiv = document.getElementById('subcategories');
  const subSubcategoriesDiv = document.getElementById('sub-subcategories');
  const submenu = document.querySelector('.sub-menu');
  submenu.style.display = 'none';
  let currentPage = 1;
  let isLoading = false;
  let hasMoreItems = true;
  let currentCategoryIndex = null;
  let isMobileView = window.innerWidth <= 768;

  const leftPositions = {
    1: '50%',
    2: '55%',
    3: '60%',
    4: '65%'
  };

  // Define icons for subcategories with correct paths
  const icons = {
    all: './assets/images/all.png',
    clothing: './assets/images/shirt.png',
    shoes: './assets/images/shoes.png',
    accessories: './assets/images/accesories.png',
    default: './assets/images/default-icon.png'
  };

  // Function to check if mobile view
  function checkMobileView() {
    isMobileView = window.innerWidth <= 768;
    return isMobileView;
  }

  // Function to handle mobile-specific behavior
  function handleMobileClick(element) {
    if (!checkMobileView()) return;

    const itemsContainer = element.nextElementSibling;
    if (!itemsContainer || !itemsContainer.classList.contains('sub-subcategories-mobile')) {
      const newContainer = document.createElement('div');
      newContainer.className = 'sub-subcategories-mobile';
      newContainer.style.display = 'none';
      element.after(newContainer);

      // Add loading indicator
      newContainer.innerHTML = '<div class="loading-spinner">Loading...</div>';
    }

    // Toggle visibility with proper error handling
    try {
      const isVisible = itemsContainer.style.display === 'block';
      itemsContainer.style.display = isVisible ? 'none' : 'block';

      // Toggle arrow
      const arrow = element.querySelector('.subcategory-arrow i');
      if (arrow) {
        arrow.classList.toggle('fa-chevron-down');
        arrow.classList.toggle('fa-chevron-up');
      }
    } catch (error) {
      console.error('Error in mobile click handler:', error);
    }
  }

  // Function to fetch subcategories
  async function fetchSubcategories(categoryIndex, page = 1) {
    try {
      // Add loading timeout for mobile devices
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Request timeout')), 15000));

      const fetchPromise = fetch(`/user/get_subcategories/${categoryIndex}/?page=${page}`);

      // Race between timeout and fetch
      const response = await Promise.race([fetchPromise, timeoutPromise]);

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      return data.results || data;
    } catch (error) {
      console.error('Error fetching subcategories:', error);
      return [];
    }
  }

  // Add this function to fetch all items from all subcategories
  async function fetchAllItems(categoryIndex) {
    try {
      const response = await fetch(`/user/get_subcategories/${categoryIndex}/`);
      if (!response.ok) throw new Error('Failed to fetch all items');
      return await response.json();
    } catch (error) {
      console.error('Error fetching all items:', error);
      return [];
    }
  }

  // Function to load subcategories
  async function loadSubcategories(categoryIndex) {
    if (isLoading) return;
    isLoading = true;

    try {
      const subcategories = await fetchSubcategories(categoryIndex, currentPage);

      if (currentPage === 1) {
        subcategoriesDiv.innerHTML = '';
        if (subSubcategoriesDiv) {
          subSubcategoriesDiv.innerHTML = '';
        }

        // Add "All" category at the beginning
        const allCategoryElement = document.createElement('a');
        allCategoryElement.href = `/category/${categoryIndex}`;
        allCategoryElement.className = 'subcategory selected-subcategory';
        allCategoryElement.style.fontWeight = '500';
        allCategoryElement.innerHTML = `
              <img src="/media/category_icons/all.png" class="subcategory-icon" />
              All
              <span class="subcategory-arrow" >
                  <i class=""></i>
              </span>
          `;

        const allSubContainer = document.createElement('div');
        allSubContainer.className = 'sub-subcategories';
        allSubContainer.style.display = 'none';

        // Add event listener for "ALL" category
        allCategoryElement.addEventListener('click', () => {
          document.querySelectorAll('.subcategory').forEach(item => {
            item.classList.remove('selected-subcategory');
            item.style.fontWeight = 'normal';
          });

          allCategoryElement.classList.add('selected-subcategory');
          allCategoryElement.style.fontWeight = '500';

          // Trigger the first subcategory automatically
          if (subcategories.length > 0 && !checkMobileView()) {
            handleSubcategoryClick(subcategories[0].id, allCategoryElement);
          }
        });

        subcategoriesDiv.appendChild(allCategoryElement);
        subcategoriesDiv.appendChild(allSubContainer);

        // Automatically trigger click on "ALL" category if not in mobile view
        // if (!checkMobileView()) {
        //   setTimeout(() => {
        //     allCategoryElement.click();
        //   }, 100);
        // }
      }

      // Create and append subcategory elements
      subcategories.forEach((subcategory, index) => {
        const subCatElement = document.createElement('div');
        subCatElement.className = 'subcategory';

        if (index === 0 && currentPage === 1 && !checkMobileView()) {
          subCatElement.classList.add('selected-subcategory');
          subCatElement.style.fontWeight = '500';
          setTimeout(() => {
            handleSubcategoryClick(subcategory.id, subCatElement);
          }, 100);
        }

        const categoryKey = subcategory?.name?.toLowerCase() || 'default';
        const iconPath = icons[categoryKey] || icons.default;

        subCatElement.innerHTML = `
              <img src="/media/${subcategory.icon_img}" class="subcategory-icon" />
              ${subcategory.name}
              <span class="subcategory-arrow">
                  <i class="fa-solid fa-chevron-down"></i>
              </span>
          `;
        subCatElement.dataset.subcategoryId = subcategory.id;

        subCatElement.addEventListener('click', () => {
          document.querySelectorAll('.subcategory').forEach(item => {
            item.classList.remove('selected-subcategory');
            item.style.fontWeight = 'normal';
          });

          subCatElement.classList.add('selected-subcategory');
          subCatElement.style.fontWeight = '500';
          handleSubcategoryClick(subcategory.id, subCatElement);
        });

        subcategoriesDiv.appendChild(subCatElement);
      });

      submenu.style.display = 'flex';
      submenu.style.left = leftPositions[categoryIndex] || '50%';

      if (hasMoreItems) {
        currentPage++;
      }

    } catch (error) {
      console.error('Error loading subcategories:', error);
    } finally {
      isLoading = false;
    }
  }

  // Add this function at the top level of your code
  function createMobileContainer(element) {
    const container = document.createElement('div');
    container.className = 'sub-subcategories-mobile';
    container.style.display = 'block';
    element.after(container);
    return container;
  }

  // Update the handleSubcategoryClick function
  async function handleSubcategoryClick(subcategoryId, element) {
    try {
      let mobileContainer;
      if (checkMobileView()) {
        console.log("sdasd")

        mobileContainer = element.nextElementSibling;
        if (!mobileContainer || !mobileContainer.classList.contains('sub-subcategories-mobile')) {
          mobileContainer = createMobileContainer(element);
        }

        if (mobileContainer.children.length > 0 && !mobileContainer.querySelector('.loading')) {
          mobileContainer.style.display = mobileContainer.style.display === 'none' ? 'block' : 'none';
          const arrow = element.querySelector('.subcategory-arrow i');
          if (arrow) {
            arrow.classList.toggle('fa-chevron-down');
            arrow.classList.toggle('fa-chevron-up');
          }
          return;
        }
      } else {
        mobileContainer = subSubcategoriesDiv;
      }

      mobileContainer.innerHTML = '<div class="loading">Loading...</div>';

      const response = await fetch(`/user/get_subcategories/${subcategoryId}/`);
      if (!response.ok) throw new Error('Failed to fetch data');

      const subSubcategories = await response.json();

      if (subSubcategories.length === 0) {
        mobileContainer.innerHTML = '<div class="no-data">No items found</div>';
        return;
      }

      let listItems = `
      <a href="/category/${subcategoryId}/" class="sub-subcategory-item" data-id="${subcategoryId}">
                  <div class="item-content">
                      All
                  </div>
              </a>
      `;
      listItems += subSubcategories.map((item, index) => `
              <a href="/category/${item.id}/" class="sub-subcategory-item ${index === 0 ? 'selected-item' : ''}" data-id="${item.id}">
                  <div class="item-content">
                      ${item.name}
                  </div>
              </a>
          `).join('');

      mobileContainer.innerHTML = `${listItems}`;

      // Add click handlers to items
      const items = mobileContainer.querySelectorAll('.sub-subcategory-item');
      items.forEach(item => {
        item.addEventListener('click', (e) => {
          e.stopPropagation();
          console.log('Clicked item:', item.dataset.id);
        });
      });

      if (window.innerWidth <= 768) {
        mobileContainer.style.display = 'block';
      }

      const arrow = element.querySelector('.subcategory-arrow i');
      if (arrow) {
        arrow.classList.remove('fa-chevron-down');
        arrow.classList.add('fa-chevron-up');
      }

    } catch (error) {
      console.error('Error:', error);
      mobileContainer.innerHTML = '<div class="error">Failed to load data. Please try again.</div>';
    }
  }

  // Add scroll event listener for infinite scroll
  subcategoriesDiv.addEventListener('scroll', () => {
    if (!hasMoreItems || isLoading) return;

    const { scrollTop, scrollHeight, clientHeight } = subcategoriesDiv;
    if (scrollTop + clientHeight >= scrollHeight - 5) {
      loadSubcategories(currentCategoryIndex);
    }
  });

  // Event listeners for main menu items with mobile support
  mainMenuItems.forEach(item => {
    item.addEventListener('click', async function (e) {
      const categoryIndex = this.getAttribute('data-index');
      currentCategoryIndex = categoryIndex;
      currentPage = 1;
      hasMoreItems = true;

      // Remove active class from all items
      mainMenuItems.forEach(i => i.querySelector('p').classList.remove('active'));
      // Add active class to clicked item
      this.querySelector('p').classList.add('active');

      await loadSubcategories(categoryIndex);

      if (checkMobileView()) {
        submenu.style.left = '50%';
        submenu.style.display = 'flex'; // Ensure submenu is visible on mobile
        e.stopPropagation();
      }
    });
  });

  // Hide submenu when mouse leaves (desktop only)
  submenu.addEventListener('mouseleave', () => {
    if (!checkMobileView()) {
      submenu.style.display = 'none';
      mainMenuItems.forEach(item => item.querySelector('p').classList.remove('active'));
    }
  });

  // Handle window resize
  window.addEventListener('resize', () => {
    checkMobileView();
    if (isMobileView) {
      submenu.style.left = '50%';
    }
  });

  // Function to hide subcategories
  function hideSubcategories() {
    submenu.style.display = 'none';
  }

  // Close menu when clicking outside (mobile only)
  document.addEventListener('click', (e) => {
    if (checkMobileView() && !submenu.contains(e.target) && !e.target.closest('.main-item')) {
      hideSubcategories();
    }
  });

  // Add these styles to your CSS
  const styles = `
      .sub-subcategories-mobile {
         
      }

      .sub-subcategory-item {
          padding: 12px;
          cursor: pointer;
          transition: font-weight 0.2s ease;
      }

      .subcategories.selected-item {
          font-weight: 500;
      }

      .sub-subcategory-item:last-child {
          border-bottom: none;
      }

      .sub-subcategory-item:hover {
         
      }

      .loading {
          text-align: center;
          padding: 20px;
          color: #666;
      }

      .error {
          color: #ff4444;
          text-align: center;
          padding: 10px;
      }

      .no-data {
          text-align: center;
          padding: 20px;
          color: #666;
      }

      .subcategory {
          transition: font-weight 0.2s ease;
      }

      .selected-subcategory {
          font-weight: 500;
      }
  `;

  // Add the styles to the document
  const styleSheet = document.createElement('style');
  styleSheet.textContent = styles;
  document.head.appendChild(styleSheet);
});