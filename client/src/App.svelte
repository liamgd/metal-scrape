<script lang="ts">
  import { ChevronRightIcon } from "svelte-feather-icons";
  import { fade } from "svelte/transition";

  const displayDigits = 2;

  let products: Array<any> = [];

  let sortAttribute = "index";
  let sortAscending = true;

  let page = 0;

  let load = () => {
    let sortDir = sortAscending ? "ascending" : "descending";
    let filterArgs = "";
    if (!materialInclusion.every(Boolean)) {
      filterArgs +=
        "&materials=" +
        materials.filter((_, index) => materialInclusion[index]).join(",");
    }
    if (!shapeInclusion.every(Boolean)) {
      filterArgs +=
        "&shapes=" +
        shapes.filter((_, index) => shapeInclusion[index]).join(",");
    }
    for (const [key, value] of Object.entries(filters)) {
      if (value === null) continue;
      filterArgs += `&${key}=${value}`;
    }

    fetch(
      `/products?page=${page}&sort=${sortAttribute}&sortdir=${sortDir}${filterArgs}`
    )
      .then((res) => res.json())
      .then((json) => (products = json));
  };
  let sort = (attribute: string) => {
    if (sortAttribute === attribute) {
      sortAscending = !sortAscending;
    } else {
      sortAttribute = attribute;
    }
    page = 0;
    load();
  };

  let loadMore = () => {
    page++;
    load();
  };

  let showFilters = false;

  let materials = [];
  let materialInclusion = [];
  let materialsPromise = fetch("/materials")
    .then((res) => res.json())
    .then((res) => {
      materials = res;
      materialInclusion = new Array(materials.length).fill(true);
    });

  let shapes = [];
  let shapeInclusion = [];
  let shapesPromise = fetch("/shapes")
    .then((res) => res.json())
    .then((res) => {
      shapes = res;
      shapeInclusion = new Array(shapes.length).fill(true);
    });
  Promise.all([materialsPromise, shapesPromise]).then(() => load());

  let toggleAll = (array: Array<boolean>) => {
    if (array.every(Boolean)) {
      return array.fill(false);
    } else {
      return array.fill(true);
    }
  };

  let filters = {
    lengthLower: null,
    lengthUpper: null,
    poundsPerFootLower: null,
    poundsPerFootUpper: null,
    priceLower: null,
    priceUpper: null,
    pricePerFootLower: null,
    pricePerFootUpper: null,
    pricePerPoundLower: null,
    pricePerPoundUpper: null,
  };
</script>

<div class="container">
  <h1>Metals Depot Scraper</h1>
  <div class="filter-container">
    <button
      class="filter-heading"
      on:click={() => (showFilters = !showFilters)}
    >
      <p>Filters</p>
      <div class="chevron" class:rotated={showFilters}>
        <ChevronRightIcon size="30" />
      </div>
    </button>
    {#if showFilters}
      <div class="filters" transition:fade={{ duration: 200 }}>
        <div class="material-filter checklist">
          <button
            on:click={() => (materialInclusion = toggleAll(materialInclusion))}
            >Materials:</button
          >
          {#each materials as material, index}
            <label>
              <input type="checkbox" bind:checked={materialInclusion[index]} />
              {material}
            </label>
          {/each}
        </div>
        <div class="shape-filter checklist">
          <button on:click={() => (shapeInclusion = toggleAll(shapeInclusion))}
            >Shapes:</button
          >
          {#each shapes as shape, index}
            <label>
              <input type="checkbox" bind:checked={shapeInclusion[index]} />
              {shape}
            </label>
          {/each}
        </div>
        <div class="input-filters">
          <div class="length-filter">
            <label>
              Length:
              <input type="number" bind:value={filters.lengthLower} />
              to
              <input type="number" bind:value={filters.lengthUpper} />
            </label>
          </div>
          <div class="pounds-foot-filter">
            <label>
              Pounds per foot:
              <input type="number" bind:value={filters.poundsPerFootLower} />
              to
              <input type="number" bind:value={filters.poundsPerFootUpper} />
            </label>
          </div>
          <div class="price-filter">
            <label>
              Price:
              <input type="number" bind:value={filters.priceLower} />
              to
              <input type="number" bind:value={filters.priceUpper} />
            </label>
          </div>
          <div class="price-foot-filter">
            <label>
              Price per foot:
              <input type="number" bind:value={filters.pricePerFootLower} />
              to
              <input type="number" bind:value={filters.pricePerFootUpper} />
            </label>
          </div>
          <div class="price-pound-filter">
            <label>
              Price per pound:
              <input type="number" bind:value={filters.pricePerPoundLower} />
              to
              <input type="number" bind:value={filters.pricePerPoundUpper} />
            </label>
          </div>
        </div>
        <button
          class="submit-filters outline-button"
          on:click={() => {
            page = 0;
            load();
          }}>Search with filters</button
        >
      </div>
    {/if}
  </div>
  <table>
    <thead>
      <tr>
        <th>
          <button on:click={() => sort("material")}>Material</button>
        </th>
        <th>
          <button on:click={() => sort("shape")}>Shape</button>
        </th>
        <th>
          <button on:click={() => sort("index")}>Cross section</button>
        </th>
        <th>
          <button on:click={() => sort("length")}>Length</button>
        </th>
        <th>
          <button on:click={() => sort("base_weight")}>Pounds per foot</button>
        </th>
        <th>
          <button on:click={() => sort("price")}>Price</button>
        </th>
        <th>
          <button on:click={() => sort("price_per_foot")}>Price per foot</button
          >
        </th>
        <th>
          <button on:click={() => sort("price_per_pound")}
            >Price per pound</button
          >
        </th>
      </tr>
    </thead>
    <tbody>
      {#each products as product}
        <tr>
          <td>{product.material}</td>
          <td>{product.shape}</td>
          <td>{product.size}</td>
          <td>{product.length} ft</td>
          <td>{product.base_weight.toFixed(displayDigits)} lbs</td>
          <td>${product.price.toFixed(displayDigits)}</td>
          <td>${product.price_per_foot.toFixed(displayDigits)}</td>
          <td>${product.price_per_pound.toFixed(displayDigits)}</td>
        </tr>
      {/each}
      {#if products.length === 0}
        <td class="no-products" colspan="8">No products found.</td>
      {/if}
    </tbody>
  </table>
  <button class="load-more outline-button" on:click={loadMore}
    >Load more items</button
  >
</div>

<style>
  .container {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    flex-direction: column;
    color: white;
    background-color: #08212b;
    padding: 4vh 0 10vh 0;
  }

  h1 {
    font-size: 3.5vh;
  }

  .filter-container {
    width: 55%;
    display: flex;
    flex-direction: column;
    margin-bottom: 3vh;
  }

  .filter-heading {
    display: flex;
    flex-direction: row;
    font-size: 2.2vh;
    align-items: center;
    margin-bottom: 1.5%;
  }

  .filter-heading p {
    margin: 0;
  }

  .chevron {
    transition: transform 0.4s;
    display: flex;
  }

  .rotated {
    transform: rotate(90deg);
  }

  .filters {
    min-width: 55%;
    display: grid;
    grid-template-columns: 1fr 1fr 1.5fr;
    justify-content: center;
    justify-items: center;
    align-content: space-between;
    align-self: center;
  }

  .checklist {
    display: flex;
    flex-direction: column;
  }

  .checklist button {
    margin-bottom: 7%;
    font-weight: 700;
  }

  .input-filters {
    display: inline-grid;
    align-items: center;
    text-align: center;
  }

  .input-filters input {
    width: 10%;
    padding: 0.75vh;
    border: none;
    border-radius: 0.75vh;
  }

  .submit-filters {
    margin: 15% 0;
    grid-column-end: 3;
  }

  table {
    table-layout: fixed;
    width: 80%;
    border-collapse: collapse;
    font-size: 1.7vh;
    border-radius: 1.5vh 1.5vh 0 0;
    overflow: hidden;
  }

  thead {
    background-color: #03a696;
    color: white;
    text-align: center;
  }

  tbody {
    text-align: center;
  }

  tbody tr {
    background-color: #012e40;
  }

  th {
    padding: 3vh 1.2vw;
  }

  td {
    padding: 1.2vw;
  }

  button {
    background: none;
    color: inherit;
    border: none;
    padding: 0;
    font: inherit;
    cursor: pointer;
    outline: inherit;
    text-align: inherit;
  }

  tbody tr:nth-of-type(even) {
    background-color: #025159;
  }

  .no-products {
    font-size: 2.3vh;
    background-color: #012e40;
  }

  .load-more {
    margin-top: 5vh;
  }

  .outline-button {
    padding: 1.3vh;
    display: flex;
    flex-direction: row;
    justify-content: center;
    font-size: 2.2vh;
    border: 3px solid white;
    border-radius: 1.5vh;
    transition: opacity 0.1s, background-color 0.1s;
  }

  .outline-button:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }

  .outline-button:active {
    opacity: 0.7;
  }
</style>
