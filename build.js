const esbuild = require('esbuild');

esbuild.build({
    entryPoints: ['src/ZombieWaveGame.tsx'], // your entry file
    bundle: true,
    minify: true,
    outfile: 'dist/bundle.js',             // output file
    sourcemap: true,                        // optional for debugging
    loader: { '.ts': 'ts', '.tsx': 'tsx', '.js': 'jsx' },
    define: { 'process.env.NODE_ENV': '"production"' }, // production mode
}).catch(() => process.exit(1));
