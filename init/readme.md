Have `node.js` for this.

Install dependencies by `npm i`, `yarn` or `pnpm i` 
(to use yarn you need to first `npm i -g yarn` and to use pnpm you need to first
`npm i -g pnpm`, but it's recommended, because you
only need to this once and those are more efficient than npm.
I recommend pnpm.)

Edit `types.ts` (Typescript).
Then whenever you want to generate the json schema, you do:
`npm run build:schema`

`init.json` should be a JSON object which starts like:

```json
{
  "$schema": "./schema.json"
}
```

Then your IDE will help you generate JSON objects that fit the schema.