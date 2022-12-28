<script lang="ts">
  import Slider from "@bulatdashiev/svelte-slider";
  import test_products from "./testProducts";

  const displayDigits = 2;

  let products: Array<any> = test_products;

  let sortAttribute = "index";
  let sortAscending = true;

  let value: number;
  let range = [0, 100];

  $: {
    let sortDir = sortAscending ? "ascending" : "descending";
    fetch(`/products?sort=${sortAttribute}&sortdir=${sortDir}`)
      .then((res) => res.json())
      .then((res) => (products = res));
  }

  let sort = (attribute: string) => {
    if (sortAttribute === attribute) {
      sortAscending = !sortAscending;
    } else {
      sortAttribute = attribute;
    }
  };
</script>

<div class="container">
  <h1>Metals Depot Scraper</h1>
  <div class="filters">
    <Slider class="slider" bind:value range />
    <input type="number" bind:value min={range[0]} max={range[1]} />
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
    </tbody>
  </table>
  <button class="load">Load more items</button>
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
    gap: 7vh;
  }

  h1 {
    font-size: 3.5vh;
  }

  .filters {
    width: 50%;
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

  .load {
    padding: 2vh;
    display: flex;
    flex-direction: row;
    justify-content: center;
    font-size: 2.2vh;
    border: 3px solid white;
    border-radius: 1.5vh;
  }
</style>
