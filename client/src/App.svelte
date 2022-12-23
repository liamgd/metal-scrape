<script lang="ts">
  import test_products from "./testProducts";

  const displayDigits = 2;

  let products: Array<any> = test_products;

  let sortAttribute = "index";
  let sortAscending = true;

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
  <table>
    <thead>
      <tr>
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
  }

  h1 {
    margin: 10vh 0;
  }

  table {
    table-layout: fixed;
    width: 80%;
    border-collapse: collapse;
    font-size: 2.3vh;
    border-radius: 1.5vh 1.5vh 0 0;
    overflow: hidden;
    margin-bottom: 25vh;
  }

  thead {
    background-color: #03a696;
    color: white;
    text-align: left;
  }

  tbody tr {
    background-color: #012e40;
    border-bottom: thin solid #999;
  }

  td,
  th {
    padding: 2vw;
    width: 20%;
  }

  td + td,
  th + th {
    width: auto;
  }

  th button {
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

  tbody tr:last-of-type {
    border-bottom: 5px solid #f28705;
  }
</style>
