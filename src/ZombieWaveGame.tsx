import React, { useState, useEffect, useRef } from "react";
import ReactDOM from "react-dom/client";

const { useState, useEffect, useRef } = React;

const ZombieWaveGame = () => {
  const canvasRef = useRef(null);
  const shopScrollRef = useRef(null);
  const buildScrollRef = useRef(null);
  const startWaveRef = useRef(null);
  const [playerId] = useState(() => `player_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

  const [gameState, setGameState] = useState('menu');
  const [wave, setWave] = useState(1);
  const [score, setScore] = useState(0);
  const [highScore, setHighScore] = useState(0);
  const [coins, setCoins] = useState(100);
  const [totalCoins, setTotalCoins] = useState(0);
  const [xp, setXp] = useState(0);
  const [level, setLevel] = useState(1);
  const [showLevelUp, setShowLevelUp] = useState(false);
  const [showShop, setShowShop] = useState(false);
  const [showBuildMenu, setShowBuildMenu] = useState(false);
  const [selectedBuild, setSelectedBuild] = useState(null);
  const [upgrades, setUpgrades] = useState([]);
  const [isMobile, setIsMobile] = useState(false);
  const [canvasWidth, setCanvasWidth] = useState(800);
  const [canvasHeight, setCanvasHeight] = useState(600);
  const [wallRotation, setWallRotation] = useState(0);
  const [selectedStructure, setSelectedStructure] = useState(null);
  const [showUpgradeMenu, setShowUpgradeMenu] = useState(false);
  const [showPauseMenu, setShowPauseMenu] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [achievements, setAchievements] = useState([]);
  const [quickBuildMode, setQuickBuildMode] = useState(false);
  const [passiveIncome, setPassiveIncome] = useState(0);
  const [baseUpgradeLevel, setBaseUpgradeLevel] = useState(0);
  const [screenShake, setScreenShake] = useState({ x: 0, y: 0, intensity: 0 });
  const [waveCountdown, setWaveCountdown] = useState(0);
  const [killStreak, setKillStreak] = useState(0);
  const [maxKillStreak, setMaxKillStreak] = useState(0);
  const [pendingLevelUps, setPendingLevelUps] = useState(0);
  const [currentUpgradeOptions, setCurrentUpgradeOptions] = useState([]);
  const [totalLevelUps, setTotalLevelUps] = useState(0);
  const [showRanges, setShowRanges] = useState(false);
  const [showAdReward, setShowAdReward] = useState(false);
  const [adRewardType, setAdRewardType] = useState(null);
  const [adLoading, setAdLoading] = useState(false);
  const [adWatched, setAdWatched] = useState(false);
  const [currentAdSlot, setCurrentAdSlot] = useState(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Ad slot mapping for different reward types
  const adSlots = {
    coins: '2155749458',
    health: '9430043749',
    powerup: '5626530106',
    revive: '3876681775',
    nuke: '2563600102'
  };

  // Set favicon from GitHub
  useEffect(() => {
    const setFavicon = () => {
      // Set page title
      document.title = 'Zombie Survival Game - LetUsTech';

      // Remove existing favicons
      const existingFavicons = document.querySelectorAll("link[rel*='icon']");
      existingFavicons.forEach(favicon => favicon.remove());

      // Add new favicon
      const link = document.createElement('link');
      link.rel = 'icon';
      link.type = 'image/png';
      link.href = 'https://raw.githubusercontent.com/letustec-oss/LetUsTech/main/favicon.png';
      document.head.appendChild(link);

      // Fallback if GitHub favicon fails
      link.onerror = () => {
        link.href = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="70" font-size="70">🎮</text></svg>';
      };
    };

    setFavicon();
  }, []);

  // Load AdSense script
  React.useEffect(() => {
    const script = document.createElement('script');
    script.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5830581574523106";
    script.async = true;
    script.crossOrigin = "anonymous";
    document.head.appendChild(script);
    
    script.onload = () => {
      console.log('✅ AdSense script loaded successfully');
      
      // Initialize display ads after script loads
      setTimeout(() => {
        try {
          const ads = document.querySelectorAll('.adsbygoogle');
          ads.forEach((ad) => {
            if (!ad.getAttribute('data-adsbygoogle-status')) {
              (window.adsbygoogle = window.adsbygoogle || []).push({});
            }
          });
          console.log('📺 Display ads initialized');
        } catch (e) {
          console.log('⚠️ Display ad initialization error:', e);
        }
      }, 1000);
    };
    
    script.onerror = () => {
      console.log('⚠️ AdSense script failed to load');
    };
    
    return () => {
      document.head.removeChild(script);
    };
  }, []);

  // Initialize display ads when game starts
  React.useEffect(() => {
    if (gameState === 'playing') {
      setTimeout(() => {
        try {
          const ads = document.querySelectorAll('.adsbygoogle');
          ads.forEach((ad) => {
            if (!ad.getAttribute('data-adsbygoogle-status')) {
              (window.adsbygoogle = window.adsbygoogle || []).push({});
            }
          });
          console.log('📺 Display ads loaded for gameplay');
        } catch (e) {
          console.log('⚠️ Display ad error:', e);
        }
      }, 500);
    }
  }, [gameState]);

  // Horizontal scroll with mouse wheel
  React.useEffect(() => {
    const handleWheel = (e, scrollContainer) => {
      if (scrollContainer) {
        e.preventDefault();
        // Scroll horizontally based on wheel delta
        scrollContainer.scrollLeft += e.deltaY;
      }
    };

    const shopScroll = shopScrollRef.current;
    const buildScroll = buildScrollRef.current;

    const shopWheelHandler = (e) => handleWheel(e, shopScroll);
    const buildWheelHandler = (e) => handleWheel(e, buildScroll);

    if (shopScroll) {
      shopScroll.addEventListener('wheel', shopWheelHandler, { passive: false });
    }
    if (buildScroll) {
      buildScroll.addEventListener('wheel', buildWheelHandler, { passive: false });
    }

    return () => {
      if (shopScroll) {
        shopScroll.removeEventListener('wheel', shopWheelHandler);
      }
      if (buildScroll) {
        buildScroll.removeEventListener('wheel', buildWheelHandler);
      }
    };
  }, [showShop, showBuildMenu]);

  React.useEffect(() => {
    gameRef.current.buildPreview.active = !!selectedBuild;
    gameRef.current.buildPreview.type = selectedBuild;
    gameRef.current.buildPreview.rotation = wallRotation;
  }, [selectedBuild, wallRotation]);

  const gameRef = useRef({
    playerId: null,
    player: {
      x: 800, y: 600, size: 20, speed: 5.5, health: 100, maxHealth: 100,
      damage: 1, fireRate: 500, bulletSpeed: 8, piercing: 0,
      lifeSteal: 0, critChance: 0, critDamage: 1.5, dashCooldown: 0,
      lastDash: 0, dashDistance: 120, rage: 0, maxRage: 100,
      hopperRange: 0, hopperLevel: 0, shield: 0, maxShield: 0, regenRate: 0,
      vampire: false, berserker: false, ricochet: 0,
      chain: false, scavenger: false, fortify: 0, lucky: false,
      ghostBullets: false, bloodlust: false, bloodlustStacks: 0,
      homingShots: false, poisonShots: false, freezeShots: false,
      splitShot: false, laserSight: false, doubleTap: false,
      clusterBomb: false, lightning: false, orbital: false, orbitalBullets: [],
      secondChance: false, secondChanceUsed: false, adrenaline: false,
      thorns: 0, phaseShift: false, xpBoost: 1, criticalAura: false,
      timeWarp: false
    },
    zombies: [],
    bullets: [],
    particles: [],
    obstacles: [],
    turrets: [],
    walls: [],
    traps: [],
    bases: [],
    coinDrops: [],
    powerUps: [],
    keys: {},
    mouseX: 400,
    mouseY: 300,
    mouseDown: false,
    lastShot: 0,
    waveActive: false,
    zombiesLeftToSpawn: 0,
    isPaused: false,
    needsWaveStart: false,
    nextWaveTime: null,
    mapWidth: 1600,
    mapHeight: 1200,
    cameraX: 0,
    cameraY: 0,
    joystick: { active: false, startX: 0, startY: 0, currentX: 0, currentY: 0, touchId: null },
    shootTouch: { active: false, x: 0, y: 0, touchId: null },
    autoShoot: false,
    moveVector: { x: 0, y: 0 },
    buildPreview: { active: false, type: null, rotation: 0 },
    rotationFlash: 0,
    stats: {
      zombiesKilled: 0,
      bulletsShot: 0,
      structuresBuilt: 0,
      coinsEarned: 0,
      turretKills: 0,
      wallsDestroyed: 0
    },
    lastIncomeTime: Date.now(),
    wavePreview: {
      zombieCount: 0,
      types: [],
      difficulty: 'Easy'
    }
  });

  const zombieTypes = {
    normal: { color: '#93c47d', speed: 1.5, health: 2, size: 15, xp: 10, score: 10, coins: 1, damage: 1, wallDamage: 2 },
    fast: { color: '#ff6b6b', speed: 3.2, health: 1, size: 12, xp: 15, score: 20, coins: 1, damage: 0.7, wallDamage: 1 },
    tank: { color: '#4a90e2', speed: 1.0, health: 8, size: 22, xp: 30, score: 50, coins: 3, damage: 2, wallDamage: 5 },
    exploder: { color: '#f39c12', speed: 2.0, health: 3, size: 18, xp: 25, score: 40, coins: 2, damage: 1.5, wallDamage: 3 },
    boss: { color: '#8e44ad', speed: 1.2, health: 50, size: 35, xp: 100, score: 200, coins: 8, damage: 3, wallDamage: 10 },
    megaboss: { color: '#c0392b', speed: 1.4, health: 150, size: 45, xp: 250, score: 500, coins: 15, damage: 5, wallDamage: 15 },
    healer: { color: '#2ecc71', speed: 1.2, health: 4, size: 16, xp: 35, score: 60, coins: 3, damage: 0.5, wallDamage: 1, healRange: 180, healAmount: 1.5, healCooldown: 90 },
    splitter: { color: '#e67e22', speed: 1.5, health: 3, size: 18, xp: 30, score: 45, coins: 2, damage: 1, wallDamage: 2, splits: 2 },
    armored: { color: '#34495e', speed: 0.8, health: 12, size: 24, xp: 40, score: 70, coins: 4, damage: 2, wallDamage: 6, armor: 3 },
    berserker: { color: '#e74c3c', speed: 1.8, health: 6, size: 20, xp: 35, score: 55, coins: 3, damage: 1.5, wallDamage: 4, rageBonus: 2 },
    necromancer: { color: '#9b59b6', speed: 1.1, health: 8, size: 26, xp: 80, score: 120, coins: 6, damage: 1, wallDamage: 3, summonCooldown: 300 },
    shielded: { color: '#16a085', speed: 1.3, health: 5, size: 19, xp: 32, score: 50, coins: 3, damage: 1.2, wallDamage: 3, hasShield: true },
    // NEW ZOMBIE TYPES
    sprinter: { color: '#ff1493', speed: 4.5, health: 0.5, size: 10, xp: 20, score: 30, coins: 2, damage: 0.5, wallDamage: 1 },
    juggernaut: { color: '#2f4f4f', speed: 0.6, health: 20, size: 28, xp: 60, score: 100, coins: 5, damage: 3, wallDamage: 8, armor: 5 },
    toxic: { color: '#00ff00', speed: 1.4, health: 4, size: 17, xp: 40, score: 65, coins: 3, damage: 1.5, wallDamage: 2, poisonCloud: true },
    teleporter: { color: '#ff00ff', speed: 2.0, health: 3, size: 15, xp: 50, score: 80, coins: 4, damage: 1, wallDamage: 2, canTeleport: true },
    vampire: { color: '#8b0000', speed: 1.6, health: 5, size: 18, xp: 45, score: 70, coins: 3, damage: 1.5, wallDamage: 3, lifesteal: 0.5 }
  };

  const upgradeOptions = [
    // Basic upgrades
    { id: 'damage', name: 'Increased Damage', desc: '+1 damage per shot', icon: '⚔️' },
    { id: 'fireRate', name: 'Rapid Fire', desc: '-75ms cooldown', icon: '🔥' },
    { id: 'health', name: 'Max Health', desc: '+25 max health', icon: '❤️' },
    { id: 'speed', name: 'Movement Speed', desc: '+0.7 speed', icon: '⚡' },
    { id: 'piercing', name: 'Piercing Shots', desc: '+1 pierced enemy', icon: '🎯' },
    { id: 'bulletSpeed', name: 'Bullet Velocity', desc: '+2 bullet speed', icon: '💨' },
    
    // Advanced shooting upgrades
    { id: 'homingShots', name: 'Homing Bullets', desc: 'Bullets track enemies', icon: '🎯' },
    { id: 'poisonShots', name: 'Poison Rounds', desc: 'DoT damage over time', icon: '☠️' },
    { id: 'freezeShots', name: 'Freeze Rounds', desc: 'Slow enemies 50%', icon: '❄️' },
    { id: 'splitShot', name: 'Split Shot', desc: 'Bullets split on hit', icon: '✂️' },
    { id: 'laserSight', name: 'Laser Sight', desc: '+20% accuracy, +10% crit', icon: '🔴' },
    { id: 'doubleTap', name: 'Double Tap', desc: 'Fire 2 shots instantly', icon: '🔫' },
    { id: 'clusterBomb', name: 'Cluster Rounds', desc: 'Bullets explode into mini-bullets', icon: '💥' },
    { id: 'lightning', name: 'Lightning Rounds', desc: 'Random lightning strikes', icon: '⚡' },
    { id: 'orbital', name: 'Orbital Bullets', desc: 'Bullets orbit around you', icon: '🌀' },
    
    // Survival upgrades
    { id: 'lifeSteal', name: 'Life Steal', desc: '+5% HP on kill', icon: '🩸' },
    { id: 'critChance', name: 'Critical Hit', desc: '+10% crit chance', icon: '💥' },
    { id: 'critDamage', name: 'Critical Power', desc: '+0.5x crit damage', icon: '💢' },
    { id: 'dash', name: 'Dash Ability', desc: 'Unlock dash (120 distance)', icon: '🌟' },
    { id: 'shield', name: 'Energy Shield', desc: '+50 shield', icon: '🛡️' },
    { id: 'regen', name: 'Regeneration', desc: '+1 HP/sec', icon: '💚' },
    { id: 'secondChance', name: 'Second Chance', desc: 'Survive fatal hit once', icon: '💫' },
    { id: 'adrenaline', name: 'Adrenaline Rush', desc: 'Speed boost when hit', icon: '💉' },
    { id: 'thorns', name: 'Thorns', desc: 'Reflect 30% damage', icon: '🌵' },
    { id: 'phaseShift', name: 'Phase Shift', desc: 'Invincible while dashing', icon: '👻' },
    
    // Special upgrades
    { id: 'multishot', name: 'Multi Shot', desc: '+2 bullets per shot', icon: '🔱' },
    { id: 'explosive', name: 'Explosive Rounds', desc: 'AoE explosions', icon: '💣' },
    { id: 'hopper', name: 'Coin Hopper', desc: 'Auto-collect coins', icon: '🧲' },
    { id: 'xpBoost', name: 'XP Multiplier', desc: '+50% XP gain', icon: '⭐' },
    { id: 'vampire', name: 'Vampiric', desc: '+10% lifesteal', icon: '🧛' },
    { id: 'berserker', name: 'Berserker', desc: 'More dmg at low HP', icon: '😡' },
    { id: 'ricochet', name: 'Ricochet', desc: 'Bullets bounce', icon: '↩️' },
    { id: 'chain', name: 'Chain Lightning', desc: 'Chain to nearby enemies', icon: '⚡' },
    { id: 'scavenger', name: 'Scavenger', desc: '+50% coins from kills', icon: '💰' },
    { id: 'fortify', name: 'Fortify', desc: '-20% damage taken (Max 3)', icon: '🛡️' },
    { id: 'lucky', name: 'Lucky Strike', desc: '15% chance 2x coins', icon: '🍀' },
    { id: 'ghostBullets', name: 'Ghost Bullets', desc: 'Pass through walls', icon: '👻' },
    { id: 'bloodlust', name: 'Bloodlust', desc: 'Speed boost per kill', icon: '💀' },
    { id: 'criticalAura', name: 'Critical Aura', desc: 'Nearby enemies take 2x dmg', icon: '🔆' },
    { id: 'timeWarp', name: 'Time Warp', desc: 'Slow all enemies 20%', icon: '⏰' }
  ];

  const shopItems = [
    { id: 'health_potion', name: 'Health Potion', desc: 'Restore 50 HP', cost: 40, icon: '🧪' },
    { id: 'damage_boost', name: 'Damage Boost', desc: '+2 Damage', cost: 80, icon: '⚔️' },
    { id: 'speed_boost', name: 'Speed Boost', desc: '+1.5 Speed', cost: 60, icon: '⚡' },
    { id: 'max_health', name: 'Max Health Up', desc: '+50 Max HP', cost: 100, icon: '❤️' },
    { id: 'repair_base', name: 'Repair Base', desc: 'Restore 100 Base HP', cost: 120, icon: '🔧' },
    { id: 'repair_all', name: 'Repair All Structures', desc: 'Full HP to walls & turrets', cost: 250, icon: '🛠️' },
    { id: 'emergency_shield', name: 'Emergency Shield', desc: 'Invincibility 5s', cost: 300, icon: '🛡️' },
    { id: 'nuke', name: 'Nuke', desc: 'Kill all zombies on screen', cost: 800, icon: '☢️' },
    { id: 'passive_income', name: 'Passive Income', desc: '+1 coin/sec', cost: 1500, icon: '💰' },
    { id: 'upgrade_base', name: 'Upgrade Base', desc: '+100 Max HP, +1 Armor', cost: 250, icon: '🏰' }
  ];

  const buildItems = [
    { id: 'base', name: 'Base', desc: '🏠 Main objective! Protect at all costs', cost: 0, icon: '🏠', color: '#f39c12', type: 'base' },
    
    // Turrets - can be placed adjacent to anything
    { id: 'turret_basic', name: 'Basic Turret', desc: 'Balanced stats (Can place next to walls/base)', cost: 80, icon: '🔫', color: '#3498db', type: 'turret', 
      stats: { damage: 2, range: 200, fireRate: 30, special: 'none' } },
    { id: 'turret_sniper', name: 'Sniper Turret', desc: 'Long range, high damage (Adjacent placement OK)', cost: 150, icon: '🎯', color: '#9b59b6', type: 'turret',
      stats: { damage: 5, range: 400, fireRate: 60, special: 'pierce' } },
    { id: 'turret_rapid', name: 'Rapid Turret', desc: 'Fast fire rate (Adjacent placement OK)', cost: 100, icon: '⚡', color: '#e67e22', type: 'turret',
      stats: { damage: 1, range: 150, fireRate: 10, special: 'none' } },
    { id: 'turret_bomber', name: 'Bomber Turret', desc: 'Explosive AoE (Adjacent placement OK)', cost: 180, icon: '💣', color: '#e74c3c', type: 'turret',
      stats: { damage: 3, range: 250, fireRate: 50, special: 'explosive' } },
    { id: 'turret_freeze', name: 'Freeze Turret', desc: 'Slows enemies (Adjacent placement OK)', cost: 120, icon: '❄️', color: '#3498db', type: 'turret',
      stats: { damage: 1, range: 180, fireRate: 25, special: 'slow' } },
    
    // Wall - Single upgradeable type
    { id: 'wall', name: 'Wall', desc: 'Click to upgrade: Wood→Stone→Metal (Press R)', cost: 30, icon: '🪵', color: '#8B4513', type: 'wall',
      stats: { health: 50, maxHealth: 50, armor: 0, tier: 1 } },
    
    { id: 'trap', name: 'Spike Trap', desc: 'Damages zombies', cost: 60, icon: '⚠️', color: '#c0392b', type: 'trap' }
  ];

  const getXpForLevel = (lvl) => Math.floor(40 * Math.pow(1.3, lvl - 1));

  useEffect(() => {
    const checkMobile = () => {
      const isMobileDevice = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth < 768;
      setIsMobile(isMobileDevice);
      
      if (isMobileDevice) {
        setCanvasWidth(Math.min(800, window.innerWidth));
        setCanvasHeight(Math.min(600, window.innerHeight - 100));
      } else {
        const maxWidth = Math.min(1200, window.innerWidth - 100);
        const maxHeight = Math.min(900, window.innerHeight - 150);
        const aspectRatio = 4 / 3;
        let width = maxWidth;
        let height = width / aspectRatio;
        if (height > maxHeight) {
          height = maxHeight;
          width = height * aspectRatio;
        }
        setCanvasWidth(Math.floor(width));
        setCanvasHeight(Math.floor(height));
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Anti-cheat: Validate game state every 5 seconds
  useEffect(() => {
    if (gameState !== 'playing') return;
    
    const validateInterval = setInterval(() => {
      const game = gameRef.current;
      
      // Check for impossible values
      if (coins < 0 || coins > 999999 || 
          score < 0 || score > 999999 ||
          game.player.damage > 100 ||
          game.player.health > game.player.maxHealth + 50) {
        console.warn('⚠️ Invalid game state detected - resetting to safe values');
        setCoins(c => Math.min(Math.max(0, c), 999999));
        setScore(s => Math.min(Math.max(0, s), 999999));
        game.player.damage = Math.min(game.player.damage, 100);
        game.player.health = Math.min(game.player.health, game.player.maxHealth);
      }
    }, 5000);
    
    return () => clearInterval(validateInterval);
  }, [gameState, coins, score]);

  useEffect(() => {
    if (gameState !== 'playing') return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let animationId;

    const createParticles = (x, y, color, count) => {
      const game = gameRef.current;
      for (let i = 0; i < count; i++) {
        game.particles.push({
          x, y,
          vx: (Math.random() - 0.5) * 6,
          vy: (Math.random() - 0.5) * 6,
          size: Math.random() * 3 + 2,
          color,
          life: 40,
          alpha: 1,
          rotation: Math.random() * Math.PI * 2,
          rotationSpeed: (Math.random() - 0.5) * 0.2
        });
      }
    };
    
    const addScreenShake = (intensity) => {
      setScreenShake({
        x: (Math.random() - 0.5) * intensity * 0.5,
        y: (Math.random() - 0.5) * intensity * 0.5,
        intensity: intensity * 0.5
      });
      setTimeout(() => setScreenShake({ x: 0, y: 0, intensity: 0 }), 80);
    };

    const checkCollision = (x, y, size, isBullet = false, isTurretBullet = false, isPlayer = false) => {
      const game = gameRef.current;
      
      for (let obs of game.obstacles) {
        if (x + size > obs.x && x - size < obs.x + obs.width &&
            y + size > obs.y && y - size < obs.y + obs.height) {
          return true;
        }
      }
      
      // Both player and turret bullets can shoot over walls
      if (isTurretBullet || isBullet) {
        return false;
      }
      
      // Player can pass through walls
      if (isPlayer) {
        return false;
      }
      
      for (let wall of game.walls) {
        if (x + size > wall.x && x - size < wall.x + wall.width &&
            y + size > wall.y && y - size < wall.y + wall.height) {
          return true;
        }
      }
      
      return false;
    };

    const startWave = (waveNum) => {
      const game = gameRef.current;
      
      // Don't start wave during initial countdown
      if (game.initialCountdownActive) {
        console.log('⚠️ Cannot start wave during initial countdown');
        return;
      }
      
      console.log(`🌊 WAVE ${waveNum} STARTING!`);
      
      // Clear any existing wave timer
      if (game.nextWaveTimer) {
        clearTimeout(game.nextWaveTimer);
        game.nextWaveTimer = null;
      }
      
      game.waveActive = true;
      
      // Balanced difficulty scaling
      let baseZombieCount = 5 + waveNum * 2; // Reduced from 3 to 2
      
      // After wave 10, moderate growth
      if (waveNum >= 10) {
        baseZombieCount = 5 + (10 * 2) + ((waveNum - 10) * 4); // Reduced from 8 to 4
      }
      
      // After wave 20, stronger growth
      if (waveNum >= 20) {
        baseZombieCount = 5 + (10 * 2) + (10 * 4) + ((waveNum - 20) * 6); // Reduced from 12 to 6
      }
      
      // After wave 30, heavy scaling
      if (waveNum >= 30) {
        baseZombieCount = 5 + (10 * 2) + (10 * 4) + (10 * 6) + ((waveNum - 30) * 10); // Reduced from 20 to 10
      }
      
      // Bonus zombies every 5 waves
      if (waveNum % 5 === 0) {
        baseZombieCount += Math.floor(waveNum * 1.5); // Reduced from 2 to 1.5
      }
      
      game.zombiesLeftToSpawn = baseZombieCount;
      
      console.log(`🌊 Wave ${waveNum} spawning ${baseZombieCount} zombies!`);
      
      // Generate next wave preview
      const nextWaveNum = waveNum + 1;
      let nextZombieCount = 5 + nextWaveNum * 3;
      if (nextWaveNum >= 10) {
        nextZombieCount = 5 + (10 * 3) + ((nextWaveNum - 10) * 5);
      }
      if (nextWaveNum > 10 && nextWaveNum % 5 === 0) {
        nextZombieCount += 10;
      }
      
      const nextWaveTypes = ['normal', 'normal', 'fast', 'tank'];
      if (nextWaveNum >= 3) nextWaveTypes.push('exploder');
      if (nextWaveNum >= 5) nextWaveTypes.push('boss');
      if (nextWaveNum >= 15) nextWaveTypes.push('megaboss');
      
      let difficulty = 'Easy';
      if (waveNum >= 15) difficulty = 'Extreme';
      else if (waveNum >= 10) difficulty = 'Hard';
      else if (waveNum >= 5) difficulty = 'Medium';
      
      const nextDifficulty = nextWaveNum >= 15 ? 'Extreme' : nextWaveNum >= 10 ? 'Hard' : nextWaveNum >= 5 ? 'Medium' : 'Easy';
      
      game.wavePreview = {
        zombieCount: nextZombieCount,
        types: nextWaveTypes,
        difficulty: nextDifficulty
      };
      
      const isValidSpawnPoint = (x, y, size) => {
        // Check if too close to base - larger safe zone
        for (let base of game.bases) {
          const dist = Math.sqrt(
            Math.pow(base.x + base.size/2 - x, 2) + 
            Math.pow(base.y + base.size/2 - y, 2)
          );
          if (dist < 400) return false; // 400 unit safe zone around base
        }
        
        // Check if inside walls
        for (let wall of game.walls) {
          if (x + size > wall.x && x - size < wall.x + wall.width &&
              y + size > wall.y && y - size < wall.y + wall.height) {
            return false;
          }
        }
        
        // Check if inside turrets
        for (let turret of game.turrets) {
          if (x + size > turret.x && x - size < turret.x + turret.size &&
              y + size > turret.y && y - size < turret.y + turret.size) {
            return false;
          }
        }
        
        // Don't spawn too close to player
        const distToPlayer = Math.sqrt(
          Math.pow(x - game.player.x, 2) + 
          Math.pow(y - game.player.y, 2)
        );
        if (distToPlayer < 250) return false; // Increased from 150
        
        return true;
      };
      
      const spawnInterval = setInterval(() => {
        if (game.zombiesLeftToSpawn > 0 && gameState === 'playing') {
          // More variety in zombie types as waves progress
          const types = ['normal', 'normal', 'fast'];
          if (waveNum >= 2) types.push('tank', 'healer');
          if (waveNum >= 3) types.push('exploder', 'splitter');
          if (waveNum >= 4) types.push('armored', 'berserker');
          if (waveNum >= 5 && Math.random() < 0.3) types.push('boss');
          if (waveNum >= 6) types.push('shielded', 'necromancer');
          if (waveNum >= 10) {
            types.push('fast', 'tank', 'exploder', 'berserker', 'armored');
            types.push('sprinter'); // NEW: Ultra fast zombie
          }
          if (waveNum >= 15 && Math.random() < 0.15) types.push('megaboss');
          if (waveNum >= 12) {
            types.push('toxic', 'teleporter'); // NEW: Special zombies
          }
          if (waveNum >= 18) {
            types.push('juggernaut', 'vampire'); // NEW: Late game zombies
          }
          
          // Boss waves
          if (waveNum % 5 === 0) {
            types.push('boss', 'boss', 'necromancer');
          }
          if (waveNum % 10 === 0 && waveNum >= 10) {
            types.push('megaboss', 'boss');
          }
          
          const type = types[Math.floor(Math.random() * types.length)];
          
          // Try to find valid spawn position
          let spawnX, spawnY;
          let attempts = 0;
          const zombieSize = zombieTypes[type].size;
          
          do {
            const edge = Math.floor(Math.random() * 4);
            switch(edge) {
              case 0: // top
                spawnX = Math.random() * game.mapWidth;
                spawnY = 0;
                break;
              case 1: // right
                spawnX = game.mapWidth;
                spawnY = Math.random() * game.mapHeight;
                break;
              case 2: // bottom
                spawnX = Math.random() * game.mapWidth;
                spawnY = game.mapHeight;
                break;
              case 3: // left
                spawnX = 0;
                spawnY = Math.random() * game.mapHeight;
                break;
            }
            attempts++;
          } while (!isValidSpawnPoint(spawnX, spawnY, zombieSize) && attempts < 20); // Increased from 10 to 20 attempts
          
          // Balanced difficulty multiplier
          let difficultyMultiplier = 1 + (waveNum * 0.12); // Reduced from 0.2 to 0.12
          
          // After wave 15, stronger HP scaling
          if (waveNum >= 15) {
            difficultyMultiplier = 1 + (15 * 0.12) + ((waveNum - 15) * 0.20); // Reduced from 0.35 to 0.20
          }
          
          // After wave 25, heavy HP
          if (waveNum >= 25) {
            difficultyMultiplier = 1 + (15 * 0.12) + (10 * 0.20) + ((waveNum - 25) * 0.30); // Reduced from 0.5 to 0.30
          }
          
          const speedMultiplier = waveNum >= 10 ? 1 + ((waveNum - 10) * 0.06) : 1; // Reduced from 0.1 to 0.06
          
          const zombie = {
            ...zombieTypes[type],
            type,
            x: spawnX,
            y: spawnY,
            health: zombieTypes[type].health * difficultyMultiplier,
            maxHealth: zombieTypes[type].health * difficultyMultiplier,
            baseSpeed: zombieTypes[type].speed * speedMultiplier,
            damage: zombieTypes[type].damage * (1 + waveNum * 0.05), // Reduced from 0.08 to 0.05
            wallDamage: zombieTypes[type].wallDamage * (1 + waveNum * 0.06), // Reduced from 0.1 to 0.06
            attackCooldown: 0,
            targetLock: null,
            preferPlayer: Math.random() < 0.3 // 30% chance to prefer player
          };
          
          game.zombies.push(zombie);
          game.zombiesLeftToSpawn--;
        } else {
          clearInterval(spawnInterval);
        }
      }, 700); // Balanced spawn rate - changed from 500ms to 700ms
    };
    
    // Store startWave function in ref for external access
    startWaveRef.current = startWave;

    const createExplosion = (x, y, radius, damage) => {
      const game = gameRef.current;
      createParticles(x, y, '#ff6600', 20);
      addScreenShake(damage * 2);
      
      game.zombies.forEach(zombie => {
        const dist = Math.sqrt(Math.pow(zombie.x - x, 2) + Math.pow(zombie.y - y, 2));
        if (dist < radius) {
          zombie.health -= damage;
        }
      });
    };

    const findBlockingWall = (fromX, fromY, toX, toY) => {
      const game = gameRef.current;
      let closestWall = null;
      let closestDist = Infinity;
      
      for (let wall of game.walls) {
        if (wall.health <= 0) continue;
        
        const wallCenterX = wall.x + wall.width / 2;
        const wallCenterY = wall.y + wall.height / 2;
        
        const distToWall = Math.sqrt(
          Math.pow(wallCenterX - fromX, 2) + 
          Math.pow(wallCenterY - fromY, 2)
        );
        
        const distFromWallToTarget = Math.sqrt(
          Math.pow(toX - wallCenterX, 2) + 
          Math.pow(toY - wallCenterY, 2)
        );
        
        const directDist = Math.sqrt(
          Math.pow(toX - fromX, 2) + 
          Math.pow(toY - fromY, 2)
        );
        
        if (distToWall + distFromWallToTarget < directDist * 1.2 && distToWall < closestDist) {
          closestDist = distToWall;
          closestWall = wall;
        }
      }
      
      return closestWall;
    };

    const checkStructureOverlap = (x, y, width, height, structureType) => {
      const game = gameRef.current;
      
      // Allow walls to touch each other, turrets can be adjacent to anything
      const buffer = structureType === 'wall' ? 0 : structureType === 'turret' ? 0 : 2;
      
      // Check overlap with walls - turrets can be right next to walls
      for (let wall of game.walls) {
        const wallBuffer = structureType === 'turret' ? -1 : (structureType === 'wall' ? 0 : buffer);
        if (x < wall.x + wall.width + wallBuffer && 
            x + width > wall.x - wallBuffer &&
            y < wall.y + wall.height + wallBuffer && 
            y + height > wall.y - wallBuffer) {
          return { valid: false, reason: 'Overlaps with wall' };
        }
      }
      
      // Check overlap with turrets - turrets can be adjacent to each other
      for (let turret of game.turrets) {
        const tSize = turret.size || 50;
        const turretBuffer = structureType === 'turret' ? -1 : buffer;
        if (x < turret.x + tSize + turretBuffer && 
            x + width > turret.x - turretBuffer &&
            y < turret.y + tSize + turretBuffer && 
            y + height > turret.y - turretBuffer) {
          return { valid: false, reason: 'Overlaps with turret' };
        }
      }
      
      // Check overlap with base - turrets can be adjacent
      for (let base of game.bases) {
        const baseBuffer = structureType === 'turret' ? -1 : buffer;
        if (x < base.x + base.size + baseBuffer && 
            x + width > base.x - baseBuffer &&
            y < base.y + base.size + baseBuffer && 
            y + height > base.y - baseBuffer) {
          return { valid: false, reason: 'Overlaps with base' };
        }
      }
      
      // Check overlap with traps - strict distance
      for (let trap of game.traps) {
        const trapDist = Math.sqrt(
          Math.pow(x + width/2 - trap.x, 2) + 
          Math.pow(y + height/2 - trap.y, 2)
        );
        if (trapDist < 40) {
          return { valid: false, reason: 'Too close to trap' };
        }
      }
      
      // Check if within map bounds with margin
      if (x < 20 || y < 20 || x + width > game.mapWidth - 20 || y + height > game.mapHeight - 20) {
        return { valid: false, reason: 'Out of bounds' };
      }
      
      return { valid: true, reason: 'OK' };
    };

    const performDash = () => {
      const game = gameRef.current;
      const now = Date.now();
      
      if (now - game.player.lastDash < game.player.dashCooldown * 1000) return;
      
      let angle;
      if (isMobile && game.shootTouch.active) {
        const worldX = game.shootTouch.x + game.cameraX;
        const worldY = game.shootTouch.y + game.cameraY;
        angle = Math.atan2(worldY - game.player.y, worldX - game.player.x);
      } else if (isMobile && (game.moveVector.x !== 0 || game.moveVector.y !== 0)) {
        angle = Math.atan2(game.moveVector.y, game.moveVector.x);
      } else {
        angle = Math.atan2(game.mouseY + game.cameraY - game.player.y, 
                           game.mouseX + game.cameraX - game.player.x);
      }
      
      const newX = game.player.x + Math.cos(angle) * game.player.dashDistance;
      const newY = game.player.y + Math.sin(angle) * game.player.dashDistance;
      
      let canDash = true;
      for (let obs of game.obstacles) {
        if (newX + game.player.size > obs.x && newX - game.player.size < obs.x + obs.width &&
            newY + game.player.size > obs.y && newY - game.player.size < obs.y + obs.height) {
          canDash = false;
          break;
        }
      }
      
      if (canDash) {
        game.player.x = Math.max(30, Math.min(game.mapWidth - 30, newX));
        game.player.y = Math.max(30, Math.min(game.mapHeight - 30, newY));
      }
      
      // Phase shift - invincibility during dash
      if (game.player.phaseShift) {
        game.player.invincible = true;
        game.player.invincibleUntil = Date.now() + 500;
        setTimeout(() => game.player.invincible = false, 500);
      }
      
      game.player.lastDash = now;
      createParticles(game.player.x, game.player.y, '#00ffff', 15);
    };

    const shootBullet = () => {
      const game = gameRef.current;
      
      const targetX = game.mouseX + game.cameraX;
      const targetY = game.mouseY + game.cameraY;
      
      const dx = targetX - game.player.x;
      const dy = targetY - game.player.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      
      if (dist === 0) return;
      
      // Laser sight increases accuracy and crit
      let critChance = game.player.critChance;
      const isCrit = Math.random() < critChance;
      let damage = game.player.damage * (isCrit ? game.player.critDamage : 1);
      
      // Berserker bonus
      if (game.player.berserker && game.player.health < game.player.maxHealth * 0.3) {
        damage *= 1.5;
      }
      
      const createBullet = (offsetAngle = 0) => {
        const finalAngle = Math.atan2(dy, dx) + offsetAngle;
        return {
          id: `bullet_${Date.now()}_${Math.random()}`,
          playerId: game.playerId,
          x: game.player.x,
          y: game.player.y,
          vx: Math.cos(finalAngle) * game.player.bulletSpeed,
          vy: Math.sin(finalAngle) * game.player.bulletSpeed,
          damage: damage,
          piercing: game.player.piercing,
          isCrit: isCrit,
          explosive: game.player.explosive || false,
          ricochet: game.player.ricochet || 0,
          hasChained: false,
          homing: game.player.homingShots || false,
          poison: game.player.poisonShots || false,
          freeze: game.player.freezeShots || false,
          split: game.player.splitShot || false,
          cluster: game.player.clusterBomb || false
        };
      };
      
      // Double tap - fire twice instantly
      const shotsToFire = game.player.doubleTap ? 2 : 1;
      
      for (let shot = 0; shot < shotsToFire; shot++) {
        const bullet = createBullet();
        game.bullets.push(bullet);
        gameRef.current.stats.bulletsShot++;
        
        // Lightning effect - random lightning strikes
        if (game.player.lightning && Math.random() < 0.15) {
          const nearbyZombies = game.zombies.filter(z => {
            const d = Math.sqrt(Math.pow(z.x - targetX, 2) + Math.pow(z.y - targetY, 2));
            return d < 200;
          });
          if (nearbyZombies.length > 0) {
            const target = nearbyZombies[Math.floor(Math.random() * nearbyZombies.length)];
            target.health -= damage * 2;
            createParticles(target.x, target.y, '#ffff00', 20);
          }
        }
        
        if (game.player.multishot) {
          const angle1 = Math.atan2(dy, dx) + 0.3;
          const angle2 = Math.atan2(dy, dx) - 0.3;
          
          game.bullets.push(createBullet(0.3));
          game.bullets.push(createBullet(-0.3));
        }
      }
    };

    const darkenColor = (color, percent) => {
      const num = parseInt(color.replace('#', ''), 16);
      const amt = Math.round(2.55 * percent);
      const R = Math.max(0, (num >> 16) - amt);
      const G = Math.max(0, (num >> 8 & 0x00FF) - amt);
      const B = Math.max(0, (num & 0x0000FF) - amt);
      return '#' + (0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1);
    };

    const lightenColor = (color, percent) => {
      const num = parseInt(color.replace('#', ''), 16);
      const amt = Math.round(2.55 * percent);
      const R = Math.min(255, (num >> 16) + amt);
      const G = Math.min(255, (num >> 8 & 0x00FF) + amt);
      const B = Math.min(255, (num & 0x0000FF) + amt);
      return '#' + (0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1);
    };

    const gameLoop = () => {
      const game = gameRef.current;
      const canvas = canvasRef.current;
      if (!canvas) return;
      
      // Animated gradient background
      const time = Date.now() / 2000;
      const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
      gradient.addColorStop(0, `hsl(${230 + Math.sin(time) * 10}, 30%, ${10 + Math.sin(time) * 2}%)`);
      gradient.addColorStop(0.5, `hsl(${250 + Math.cos(time) * 10}, 25%, ${15 + Math.cos(time) * 2}%)`);
      gradient.addColorStop(1, `hsl(${270 + Math.sin(time * 0.7) * 10}, 20%, ${12 + Math.sin(time * 0.7) * 2}%)`);
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Subtle starfield effect
      for (let i = 0; i < 30; i++) {
        const starX = (i * 73) % canvas.width;
        const starY = (i * 127) % canvas.height;
        const twinkle = Math.sin(time * 3 + i) * 0.5 + 0.5;
        ctx.fillStyle = `rgba(255, 255, 255, ${0.2 * twinkle})`;
        ctx.fillRect(starX, starY, 1, 1);
      }
      
      // Apply minimal screen shake
      if (screenShake.intensity > 0) {
        ctx.save();
        ctx.translate(screenShake.x * 0.5, screenShake.y * 0.5);
      }
      
      if (game.needsWaveStart && game.bases.length > 0 && !game.waveActive && gameState === 'playing' && !game.isPaused) {
        console.log('🌊 Wave starting in 10s...');
        game.needsWaveStart = false;
        setTimeout(() => startWave(wave), 10000);
      }
      
      if (gameState !== 'playing' || game.isPaused) {
        animationId = requestAnimationFrame(gameLoop);
        return;
      }

      // Regeneration
      if (game.player.regenRate > 0) {
        game.player.health = Math.min(game.player.maxHealth, game.player.health + game.player.regenRate / 60);
      }

      const targetCameraX = Math.max(0, Math.min(game.mapWidth - canvas.width, game.player.x - canvas.width/2));
      const targetCameraY = Math.max(0, Math.min(game.mapHeight - canvas.height, game.player.y - canvas.height/2));
      game.cameraX += (targetCameraX - game.cameraX) * 0.1;
      game.cameraY += (targetCameraY - game.cameraY) * 0.1;

      // Apply bloodlust speed boost
      const bloodlustBonus = game.player.bloodlust ? (game.player.bloodlustStacks || 0) * 0.2 : 0;
      const moveSpeed = game.player.speed + bloodlustBonus;
      let newX = game.player.x;
      let newY = game.player.y;
      
      if (game.keys['w'] || game.keys['ArrowUp']) newY -= moveSpeed;
      if (game.keys['s'] || game.keys['ArrowDown']) newY += moveSpeed;
      if (game.keys['a'] || game.keys['ArrowLeft']) newX -= moveSpeed;
      if (game.keys['d'] || game.keys['ArrowRight']) newX += moveSpeed;
      
      if (game.joystick.active) {
        const dx = game.joystick.currentX - game.joystick.startX;
        const dy = game.joystick.currentY - game.joystick.startY;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance > 10) {
          const normalized = Math.min(distance / 50, 1);
          newX += (dx / distance) * moveSpeed * normalized;
          newY += (dy / distance) * moveSpeed * normalized;
          
          game.moveVector.x = dx / distance;
          game.moveVector.y = dy / distance;
        }
      } else {
        game.moveVector.x = 0;
        game.moveVector.y = 0;
      }
      
      if (!checkCollision(newX, game.player.y, game.player.size, false, false, true)) {
        game.player.x = Math.max(30, Math.min(game.mapWidth - 30, newX));
      }
      if (!checkCollision(game.player.x, newY, game.player.size, false, false, true)) {
        game.player.y = Math.max(30, Math.min(game.mapHeight - 30, newY));
      }

      if (isMobile && game.shootTouch.active) {
        const now = Date.now();
        if (now - game.lastShot > game.player.fireRate) {
          game.mouseX = game.shootTouch.x;
          game.mouseY = game.shootTouch.y;
          shootBullet();
          game.lastShot = now;
        }
      }

      if (!isMobile && game.mouseDown && !game.isPaused) {
        const now = Date.now();
        if (now - game.lastShot > game.player.fireRate) {
          shootBullet();
          game.lastShot = now;
        }
      }

      game.coinDrops = game.coinDrops.filter(coin => {
        coin.lifetime--;
        const dist = Math.sqrt(
          Math.pow(coin.x - game.player.x, 2) + 
          Math.pow(coin.y - game.player.y, 2)
        );
        
        const defaultMagnetRange = 120;
        const hopperRange = game.player.hopperRange || 0;
        const effectiveRange = Math.max(defaultMagnetRange, hopperRange);
        
        if (dist < effectiveRange && dist > 30) {
          const dx = game.player.x - coin.x;
          const dy = game.player.y - coin.y;
          const speed = hopperRange > 0 ? 8 : 5;
          coin.x += (dx / dist) * speed;
          coin.y += (dy / dist) * speed;
        }
        
        if (dist < 30) {
          setCoins(c => c + coin.value);
          setTotalCoins(tc => tc + coin.value);
          gameRef.current.stats.coinsEarned += coin.value;
          createParticles(coin.x, coin.y, hopperRange > 0 ? '#00ff00' : '#ffd700', hopperRange > 0 ? 8 : 5);
          return false;
        }
        
        return coin.lifetime > 0;
      });

      // Power-up collection
      game.powerUps = game.powerUps.filter(powerUp => {
        powerUp.lifetime--;
        
        const dist = Math.sqrt(
          Math.pow(powerUp.x - game.player.x, 2) + 
          Math.pow(powerUp.y - game.player.y, 2)
        );
        
        if (dist < 40) {
          // Apply power-up effect
          switch (powerUp.type) {
            case 'health':
              game.player.health = Math.min(game.player.maxHealth, game.player.health + 50);
              createParticles(powerUp.x, powerUp.y, '#e74c3c', 15);
              break;
            case 'speed':
              game.player.speed += 0.5;
              setTimeout(() => game.player.speed -= 0.5, 10000);
              createParticles(powerUp.x, powerUp.y, '#3498db', 15);
              break;
            case 'damage':
              game.player.damage += 2;
              setTimeout(() => game.player.damage -= 2, 10000);
              createParticles(powerUp.x, powerUp.y, '#f39c12', 15);
              break;
            case 'firerate':
              const oldRate = game.player.fireRate;
              game.player.fireRate = Math.max(50, game.player.fireRate * 0.5);
              setTimeout(() => game.player.fireRate = oldRate, 10000);
              createParticles(powerUp.x, powerUp.y, '#9b59b6', 15);
              break;
            case 'coins':
              setCoins(c => c + 25);
              setTotalCoins(tc => tc + 25);
              createParticles(powerUp.x, powerUp.y, '#ffd700', 20);
              break;
          }
          return false;
        }
        
        return powerUp.lifetime > 0;
      });

      // Passive income generation
      const now = Date.now();
      if (passiveIncome > 0 && now - game.lastIncomeTime >= 1000) {
        setCoins(c => c + passiveIncome);
        setTotalCoins(tc => tc + passiveIncome);
        gameRef.current.stats.coinsEarned += passiveIncome;
        game.lastIncomeTime = now;
        createParticles(game.player.x, game.player.y - 30, '#00ff00', 3);
      }

      game.bullets = game.bullets.filter(bullet => {
        const oldX = bullet.x;
        const oldY = bullet.y;
        
        // Homing bullets track nearest zombie
        if (bullet.homing && !bullet.fromTurret) {
          let closestZombie = null;
          let closestDist = 300;
          
          game.zombies.forEach(zombie => {
            const dist = Math.sqrt(
              Math.pow(zombie.x - bullet.x, 2) + 
              Math.pow(zombie.y - bullet.y, 2)
            );
            if (dist < closestDist) {
              closestDist = dist;
              closestZombie = zombie;
            }
          });
          
          if (closestZombie) {
            const dx = closestZombie.x - bullet.x;
            const dy = closestZombie.y - bullet.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist > 0) {
              const homingStrength = 0.3;
              bullet.vx += (dx / dist) * homingStrength;
              bullet.vy += (dy / dist) * homingStrength;
              
              // Normalize speed
              const currentSpeed = Math.sqrt(bullet.vx * bullet.vx + bullet.vy * bullet.vy);
              bullet.vx = (bullet.vx / currentSpeed) * game.player.bulletSpeed;
              bullet.vy = (bullet.vy / currentSpeed) * game.player.bulletSpeed;
            }
          }
        }
        
        bullet.x += bullet.vx;
        bullet.y += bullet.vy;
        
        // Ghost bullets ignore wall collisions
        const ignoreWalls = game.player.ghostBullets && !bullet.fromTurret;
        if (checkCollision(bullet.x, bullet.y, 3, true, bullet.fromTurret) && !ignoreWalls) {
          if (bullet.explosive) {
            createExplosion(oldX, oldY, 50, bullet.damage * 0.5);
          }
          // Ricochet
          if (bullet.ricochet > 0) {
            bullet.vx *= -1;
            bullet.vy *= -1;
            bullet.ricochet--;
            return true;
          }
          return false;
        }
        
        return bullet.x > 0 && bullet.x < game.mapWidth && bullet.y > 0 && bullet.y < game.mapHeight;
      });

      game.turrets.forEach(turret => {
        turret.cooldown--;
        
        if (turret.cooldown <= 0) {
          const turretSize = turret.size || 50;
          const centerX = turret.x + turretSize / 2;
          const centerY = turret.y + turretSize / 2;
          
          let closestZombie = null;
          let closestDist = turret.range;
          
          game.zombies.forEach(zombie => {
            const dist = Math.sqrt(
              Math.pow(zombie.x - centerX, 2) + 
              Math.pow(zombie.y - centerY, 2)
            );
            
            if (dist < closestDist) {
              closestDist = dist;
              closestZombie = zombie;
            }
          });
          
          if (closestZombie) {
            const dx = closestZombie.x - centerX;
            const dy = closestZombie.y - centerY;
            const dist = Math.sqrt(dx * dx + dy * dy);
            
            const angle = Math.atan2(dy, dx);
            const spawnDistance = turretSize / 2;
            const spawnX = centerX + Math.cos(angle) * spawnDistance;
            const spawnY = centerY + Math.sin(angle) * spawnDistance;
            
            const bullet = {
              x: spawnX,
              y: spawnY,
              vx: (dx / dist) * 10,
              vy: (dy / dist) * 10,
              damage: turret.damage,
              piercing: turret.special === 'pierce' ? 2 : 0,
              isCrit: false,
              explosive: turret.special === 'explosive',
              fromTurret: true,
              turretType: turret.turretType,
              ricochet: 0
            };
            
            game.bullets.push(bullet);
            createParticles(spawnX, spawnY, turret.color || '#00ff88', 3);
            
            if (turret.special === 'slow' && closestZombie) {
              closestZombie.slowedUntil = Date.now() + 2000;
            }
            
            turret.cooldown = turret.fireRate;
            turret.lastShotTime = Date.now();
          }
        }
      });

      game.traps.forEach(trap => {
        trap.cooldown--;
        
        game.zombies.forEach(zombie => {
          const dist = Math.sqrt(
            Math.pow(zombie.x - trap.x, 2) + 
            Math.pow(zombie.y - trap.y, 2)
          );
          
          if (dist < 30 && trap.cooldown <= 0) {
            zombie.health -= 1;
            trap.cooldown = 20;
            createParticles(trap.x, trap.y, '#e74c3c', 5);
          }
        });
      });

      // ENHANCED ZOMBIE AI WITH PLAYER TARGETING
      game.zombies.forEach(zombie => {
        // Process status effects
        if (zombie.poisoned && zombie.poisonDuration > 0) {
          zombie.poisonDuration--;
          zombie.health -= zombie.poisonDamage;
          if (zombie.poisonDuration % 20 === 0) {
            createParticles(zombie.x, zombie.y, '#00ff00', 3);
          }
          if (zombie.poisonDuration <= 0) {
            zombie.poisoned = false;
          }
        }
        
        if (zombie.frozen && Date.now() < zombie.frozenUntil) {
          // Zombie is frozen, skip AI this frame
          createParticles(zombie.x, zombie.y, '#00ffff', 1);
          return;
        } else if (zombie.frozen) {
          zombie.frozen = false;
        }
        
        // Special zombie abilities
        if (zombie.type === 'healer') {
          // Initialize heal cooldown if not set
          if (zombie.healCooldown === undefined) {
            zombie.healCooldown = 0;
          }
          
          if (zombie.healCooldown <= 0) {
            // Heal nearby zombies
            let healedCount = 0;
            game.zombies.forEach(other => {
              if (other !== zombie) {
                const dist = Math.sqrt(
                  Math.pow(zombie.x - other.x, 2) + 
                  Math.pow(zombie.y - other.y, 2)
                );
                
                // Heal zombies within range that are damaged
                if (dist < zombie.healRange && other.health < other.maxHealth) {
                  const healAmount = Math.min(zombie.healAmount, other.maxHealth - other.health);
                  other.health += healAmount;
                  healedCount++;
                  
                  // Create healing particles
                  createParticles(other.x, other.y, '#2ecc71', 8);
                  
                  // Visual healing beam
                  game.particles.push({
                    x: zombie.x,
                    y: zombie.y,
                    vx: (other.x - zombie.x) / 30,
                    vy: (other.y - zombie.y) / 30,
                    size: 3,
                    color: '#00ff88',
                    life: 30,
                    alpha: 1,
                    rotation: 0,
                    rotationSpeed: 0
                  });
                }
              }
            });
            
            // Reset cooldown if healed someone
            if (healedCount > 0) {
              zombie.healCooldown = zombieTypes.healer.healCooldown;
              // Visual feedback on healer
              createParticles(zombie.x, zombie.y, '#2ecc71', 15);
            }
          } else {
            zombie.healCooldown--;
          }
        }
        
        if (zombie.type === 'berserker') {
          // Speed up as health decreases
          const healthPercent = zombie.health / zombie.maxHealth;
          zombie.baseSpeed = zombieTypes.berserker.speed * (1 + (1 - healthPercent) * zombie.rageBonus);
        }
        
        if (zombie.type === 'necromancer' && !zombie.summonCooldownActive && game.zombies.length < 50) {
          zombie.summonCooldownActive = true;
          setTimeout(() => {
            if (game.zombies.includes(zombie)) {
              // Summon 2 normal zombies nearby
              for (let i = 0; i < 2; i++) {
                const angle = Math.random() * Math.PI * 2;
                game.zombies.push({
                  ...zombieTypes.normal,
                  type: 'normal',
                  x: zombie.x + Math.cos(angle) * 50,
                  y: zombie.y + Math.sin(angle) * 50,
                  health: 2,
                  maxHealth: 2,
                  baseSpeed: 1.2,
                  targetLock: zombie.targetLock
                });
              }
              createParticles(zombie.x, zombie.y, '#9b59b6', 15);
            }
            zombie.summonCooldownActive = false;
          }, zombie.summonCooldown * 16.67); // Convert frames to ms
        }
        
        if (!zombie.lastPosition) {
          zombie.lastPosition = { x: zombie.x, y: zombie.y, time: Date.now() };
          zombie.stuckCounter = 0;
        }
        
        const timeSinceLastCheck = Date.now() - zombie.lastPosition.time;
        if (timeSinceLastCheck > 2000) {
          const distMoved = Math.sqrt(
            Math.pow(zombie.x - zombie.lastPosition.x, 2) + 
            Math.pow(zombie.y - zombie.lastPosition.y, 2)
          );
          
          if (distMoved < 20) {
            zombie.stuckCounter++;
            if (zombie.stuckCounter >= 3) {
              const angle = Math.random() * Math.PI * 2;
              const distance = 100 + Math.random() * 50;
              zombie.x += Math.cos(angle) * distance;
              zombie.y += Math.sin(angle) * distance;
              zombie.x = Math.max(50, Math.min(game.mapWidth - 50, zombie.x));
              zombie.y = Math.max(50, Math.min(game.mapHeight - 50, zombie.y));
              zombie.stuckCounter = 0;
            }
          } else {
            zombie.stuckCounter = 0;
          }
          
          zombie.lastPosition = { x: zombie.x, y: zombie.y, time: Date.now() };
        }
        
        const currentSpeed = (zombie.slowedUntil && Date.now() < zombie.slowedUntil) 
          ? zombie.baseSpeed * 0.5 
          : zombie.baseSpeed;
        
        // Time warp global slow
        const finalSpeed = game.player.timeWarp ? currentSpeed * 0.8 : currentSpeed;
        
        // SMART TARGETING SYSTEM
        let targetX = game.player.x;
        let targetY = game.player.y;
        let targetType = 'player';
        let targetObject = null;
        let closestDist = Infinity;
        
        // Some zombies prefer the player
        if (zombie.preferPlayer) {
          const distToPlayer = Math.sqrt(
            Math.pow(game.player.x - zombie.x, 2) + 
            Math.pow(game.player.y - zombie.y, 2)
          );
          closestDist = distToPlayer;
          
          // Check if wall blocks path to player
          const blockingWall = findBlockingWall(zombie.x, zombie.y, game.player.x, game.player.y);
          if (blockingWall) {
            const distToWall = Math.sqrt(
              Math.pow(blockingWall.x + blockingWall.width/2 - zombie.x, 2) + 
              Math.pow(blockingWall.y + blockingWall.height/2 - zombie.y, 2)
            );
            closestDist = distToWall;
            targetX = blockingWall.x + blockingWall.width/2;
            targetY = blockingWall.y + blockingWall.height/2;
            targetType = 'wall';
            targetObject = blockingWall;
          }
        } else {
          // Priority 1: Base (if exists and alive)
          if (game.bases.length > 0 && game.bases[0].health > 0) {
            const base = game.bases[0];
            const baseCenterX = base.x + base.size/2;
            const baseCenterY = base.y + base.size/2;
            
            const blockingWall = findBlockingWall(zombie.x, zombie.y, baseCenterX, baseCenterY);
            
            if (blockingWall) {
              const distToWall = Math.sqrt(
                Math.pow(blockingWall.x + blockingWall.width/2 - zombie.x, 2) + 
                Math.pow(blockingWall.y + blockingWall.height/2 - zombie.y, 2)
              );
              closestDist = distToWall;
              targetX = blockingWall.x + blockingWall.width/2;
              targetY = blockingWall.y + blockingWall.height/2;
              targetType = 'wall';
              targetObject = blockingWall;
            } else {
              const distToBase = Math.sqrt(
                Math.pow(baseCenterX - zombie.x, 2) + 
                Math.pow(baseCenterY - zombie.y, 2)
              );
              closestDist = distToBase;
              targetX = baseCenterX;
              targetY = baseCenterY;
              targetType = 'base';
              targetObject = base;
            }
          } else {
            // Priority 2: Turrets
            for (let turret of game.turrets) {
              if (turret.health > 0) {
                const turretCenterX = turret.x + turret.size/2;
                const turretCenterY = turret.y + turret.size/2;
                
                const blockingWall = findBlockingWall(zombie.x, zombie.y, turretCenterX, turretCenterY);
                
                if (blockingWall) {
                  const distToWall = Math.sqrt(
                    Math.pow(blockingWall.x + blockingWall.width/2 - zombie.x, 2) + 
                    Math.pow(blockingWall.y + blockingWall.height/2 - zombie.y, 2)
                  );
                  if (distToWall < closestDist) {
                    closestDist = distToWall;
                    targetX = blockingWall.x + blockingWall.width/2;
                    targetY = blockingWall.y + blockingWall.height/2;
                    targetType = 'wall';
                    targetObject = blockingWall;
                  }
                } else {
                  const distToTurret = Math.sqrt(
                    Math.pow(turretCenterX - zombie.x, 2) + 
                    Math.pow(turretCenterY - zombie.y, 2)
                  );
                  if (distToTurret < closestDist) {
                    closestDist = distToTurret;
                    targetX = turretCenterX;
                    targetY = turretCenterY;
                    targetType = 'turret';
                    targetObject = turret;
                  }
                }
              }
            }
            
            // Priority 3: Walls (if close by)
            if (!targetObject || targetType === 'player') {
              for (let wall of game.walls) {
                if (wall.health > 0) {
                  const wallCenterX = wall.x + wall.width/2;
                  const wallCenterY = wall.y + wall.height/2;
                  const distToWall = Math.sqrt(
                    Math.pow(wallCenterX - zombie.x, 2) + 
                    Math.pow(wallCenterY - zombie.y, 2)
                  );
                  
                  if (distToWall < 150 && distToWall < closestDist) {
                    closestDist = distToWall;
                    targetX = wallCenterX;
                    targetY = wallCenterY;
                    targetType = 'wall';
                    targetObject = wall;
                  }
                }
              }
            }
            
            // Priority 4: Player (default)
            if (!targetObject) {
              const distToPlayer = Math.sqrt(
                Math.pow(game.player.x - zombie.x, 2) + 
                Math.pow(game.player.y - zombie.y, 2)
              );
              if (distToPlayer < closestDist) {
                closestDist = distToPlayer;
              }
            }
          }
        }
        
        const dx = targetX - zombie.x;
        const dy = targetY - zombie.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        zombie.targetLock = targetType;
        
        // Movement
        if (dist > 0) {
          let moveX = (dx / dist) * finalSpeed;
          let moveY = (dy / dist) * finalSpeed;
          
          const newX = zombie.x + moveX;
          const newY = zombie.y + moveY;
          
          // Check collision with walls - zombies cannot pass through walls
          let canMoveX = true;
          let canMoveY = true;
          
          // Check wall collisions
          for (let wall of game.walls) {
            if (wall.health > 0) {
              // Check X movement
              if (newX + zombie.size > wall.x && newX - zombie.size < wall.x + wall.width &&
                  zombie.y + zombie.size > wall.y && zombie.y - zombie.size < wall.y + wall.height) {
                canMoveX = false;
              }
              
              // Check Y movement
              if (zombie.x + zombie.size > wall.x && zombie.x - zombie.size < wall.x + wall.width &&
                  newY + zombie.size > wall.y && newY - zombie.size < wall.y + wall.height) {
                canMoveY = false;
              }
            }
          }
          
          // Check obstacle collisions
          if (!checkCollision(newX, zombie.y, zombie.size)) {
            canMoveX = canMoveX && true;
          } else {
            canMoveX = false;
          }
          
          if (!checkCollision(zombie.x, newY, zombie.size)) {
            canMoveY = canMoveY && true;
          } else {
            canMoveY = false;
          }
          
          if (!canMoveX && !canMoveY) {
            // Try diagonal movement if stuck
            const angle = Math.atan2(dy, dx) + (Math.random() - 0.5) * Math.PI / 2;
            moveX = Math.cos(angle) * currentSpeed;
            moveY = Math.sin(angle) * currentSpeed;
            
            const diagX = zombie.x + moveX;
            const diagY = zombie.y + moveY;
            
            canMoveX = !checkCollision(diagX, zombie.y, zombie.size);
            canMoveY = !checkCollision(zombie.x, diagY, zombie.size);
            
            // Double check walls for diagonal movement
            for (let wall of game.walls) {
              if (wall.health > 0) {
                if (diagX + zombie.size > wall.x && diagX - zombie.size < wall.x + wall.width &&
                    zombie.y + zombie.size > wall.y && zombie.y - zombie.size < wall.y + wall.height) {
                  canMoveX = false;
                }
                if (zombie.x + zombie.size > wall.x && zombie.x - zombie.size < wall.x + wall.width &&
                    diagY + zombie.size > wall.y && diagY - zombie.size < wall.y + wall.height) {
                  canMoveY = false;
                }
              }
            }
            
            if (canMoveX) zombie.x = diagX;
            if (canMoveY) zombie.y = diagY;
          } else {
            if (canMoveX) zombie.x = newX;
            if (canMoveY) zombie.y = newY;
          }
        }
        
        // ATTACK LOGIC
        zombie.attackCooldown = Math.max(0, zombie.attackCooldown - 1);
        
        if (targetType === 'base' && closestDist < 60 && zombie.attackCooldown === 0) {
          const base = game.bases[0];
          const actualDamage = Math.max(1, zombie.damage - (base.armor || 0));
          base.health -= actualDamage;
          zombie.attackCooldown = 30;
          createParticles(base.x + base.size/2, base.y + base.size/2, '#ff6600', 5);
          
          if (base.health <= 0) {
            game.bases = [];
            createParticles(base.x + base.size/2, base.y + base.size/2, '#ff0000', 30);
            setGameState('gameover');
          }
        } else if (targetType === 'turret' && closestDist < 60 && zombie.attackCooldown === 0) {
          const turretDamage = zombie.damage;
          targetObject.health -= turretDamage;
          zombie.attackCooldown = 30;
          createParticles(targetObject.x + targetObject.size/2, targetObject.y + targetObject.size/2, '#ff6600', 8);
          
          if (targetObject.health <= 0) {
            game.turrets = game.turrets.filter(t => t !== targetObject);
            createParticles(targetObject.x + targetObject.size/2, targetObject.y + targetObject.size/2, '#95a5a6', 20);
            game.coinDrops.push({
              x: targetObject.x + targetObject.size/2,
              y: targetObject.y + targetObject.size/2,
              value: 5, // Reduced from 10
              lifetime: 300
            });
          }
        } else if (targetType === 'wall' && closestDist < 50 && zombie.attackCooldown === 0) {
          // Use wallDamage property for walls
          const wallDamageDealt = Math.max(zombie.wallDamage * 0.5, zombie.wallDamage - (targetObject.armor || 0));
          targetObject.health -= wallDamageDealt;
          zombie.attackCooldown = 30;
          createParticles(targetObject.x + targetObject.width/2, targetObject.y + targetObject.height/2, '#ff8800', 5);
          
          // Show damage number
          game.particles.push({
            x: targetObject.x + targetObject.width/2,
            y: targetObject.y + targetObject.height/2 - 20,
            vx: 0,
            vy: -1,
            size: 12,
            color: '#ff0000',
            life: 40,
            alpha: 1,
            rotation: 0,
            rotationSpeed: 0,
            isText: true,
            text: `-${Math.floor(wallDamageDealt)}`
          });
          
          if (targetObject.health <= 0) {
            game.walls = game.walls.filter(w => w !== targetObject);
            gameRef.current.stats.wallsDestroyed++;
            createParticles(targetObject.x + targetObject.width/2, targetObject.y + targetObject.height/2, targetObject.color || '#95a5a6', 20);
            const salvage = Math.floor((targetObject.tier || 1) * 3); // Reduced from 5
            game.coinDrops.push({
              x: targetObject.x + targetObject.width/2,
              y: targetObject.y + targetObject.height/2,
              value: salvage,
              lifetime: 300
            });
          }
        } else if (targetType === 'player' && closestDist < 30) {
          // Attack player with fortify damage reduction
          let damageToPlayer = zombie.damage;
          if (game.player.fortify > 0) {
            damageToPlayer *= (1 - game.player.fortify);
          }
          
          // Thorns damage reflection
          if (game.player.thorns > 0) {
            zombie.health -= zombie.damage * game.player.thorns;
            createParticles(zombie.x, zombie.y, '#ff0000', 5);
          }
          
          // Adrenaline rush - speed boost when hit
          if (game.player.adrenaline) {
            game.player.speed += 0.5;
            setTimeout(() => game.player.speed -= 0.5, 2000);
          }
          
          if (game.player.shield > 0) {
            game.player.shield -= damageToPlayer;
            if (game.player.shield < 0) {
              game.player.health += game.player.shield; // Overflow damage
              game.player.shield = 0;
            }
          } else {
            game.player.health -= damageToPlayer;
          }
          
          // Second chance - survive fatal hit
          if (game.player.health <= 0 && !game.player.invincible) {
            if (game.player.secondChance && !game.player.secondChanceUsed) {
              game.player.health = game.player.maxHealth * 0.5;
              game.player.secondChanceUsed = true;
              createParticles(game.player.x, game.player.y, '#ffff00', 30);
            } else {
              setGameState('gameover');
            }
          }
        }
      });
      
      // Orbital bullets system
      if (game.player.orbital && game.player.orbitalBullets.length > 0) {
        game.player.orbitalBullets.forEach((orbital, idx) => {
          orbital.angle += 0.05;
          const orbitalX = game.player.x + Math.cos(orbital.angle) * orbital.distance;
          const orbitalY = game.player.y + Math.sin(orbital.angle) * orbital.distance;
          
          // Check collision with zombies
          game.zombies.forEach(zombie => {
            const dist = Math.sqrt(
              Math.pow(zombie.x - orbitalX, 2) + 
              Math.pow(zombie.y - orbitalY, 2)
            );
            if (dist < zombie.size + 10) {
              zombie.health -= game.player.damage * 0.5;
              createParticles(zombie.x, zombie.y, '#00ffff', 5);
            }
          });
        });
      }

      // Bullet hits
      game.bullets.forEach((bullet, bulletIndex) => {
        game.zombies.forEach((zombie, zombieIndex) => {
          const dist = Math.sqrt(
            Math.pow(bullet.x - zombie.x, 2) + 
            Math.pow(bullet.y - zombie.y, 2)
          );
          
          if (dist < zombie.size) {
            // Critical aura bonus
            let finalDamage = bullet.damage;
            if (game.player.criticalAura) {
              const distToPlayer = Math.sqrt(
                Math.pow(zombie.x - game.player.x, 2) + 
                Math.pow(zombie.y - game.player.y, 2)
              );
              if (distToPlayer < 200) {
                finalDamage *= 2;
              }
            }
            
            // Armor damage reduction for armored zombies
            if (zombie.type === 'armored' && zombie.armor) {
              finalDamage = Math.max(0.5, finalDamage - zombie.armor);
            }
            
            // Shield blocking for shielded zombies (50% chance to block)
            if (zombie.type === 'shielded' && zombie.hasShield && Math.random() < 0.5) {
              finalDamage *= 0.3;
              createParticles(zombie.x, zombie.y, '#16a085', 5);
            }
            
            zombie.health -= finalDamage;
            bullet.piercing--;
            
            // Apply status effects
            if (bullet.poison) {
              zombie.poisoned = true;
              zombie.poisonDuration = 180; // 3 seconds
              zombie.poisonDamage = bullet.damage * 0.1;
            }
            
            if (bullet.freeze) {
              zombie.frozen = true;
              zombie.frozenUntil = Date.now() + 2000;
            }
            
            // Split shot - create 2 smaller bullets
            if (bullet.split && !bullet.hasSplit) {
              bullet.hasSplit = true;
              const angle = Math.atan2(bullet.vy, bullet.vx);
              for (let i = 0; i < 2; i++) {
                const splitAngle = angle + (i === 0 ? 0.5 : -0.5);
                game.bullets.push({
                  id: `bullet_${Date.now()}_${Math.random()}`,
                  playerId: game.playerId,
                  x: bullet.x,
                  y: bullet.y,
                  vx: Math.cos(splitAngle) * game.player.bulletSpeed * 0.7,
                  vy: Math.sin(splitAngle) * game.player.bulletSpeed * 0.7,
                  damage: bullet.damage * 0.5,
                  piercing: 0,
                  isCrit: false,
                  explosive: false,
                  ricochet: 0,
                  hasChained: false,
                  hasSplit: true
                });
              }
            }
            
            // Cluster bomb - create mini bullets on hit
            if (bullet.cluster && !bullet.hasClustered) {
              bullet.hasClustered = true;
              for (let i = 0; i < 6; i++) {
                const angle = (i / 6) * Math.PI * 2;
                game.bullets.push({
                  id: `bullet_${Date.now()}_${Math.random()}`,
                  playerId: game.playerId,
                  x: bullet.x,
                  y: bullet.y,
                  vx: Math.cos(angle) * 4,
                  vy: Math.sin(angle) * 4,
                  damage: bullet.damage * 0.3,
                  piercing: 0,
                  isCrit: false,
                  explosive: false,
                  ricochet: 0,
                  hasChained: false,
                  hasClustered: true
                });
              }
              createParticles(bullet.x, bullet.y, '#ff6600', 15);
            }
            
            // Chain Lightning effect
            if (game.player.chain && !bullet.hasChained) {
              bullet.hasChained = true;
              const chainRange = 150;
              game.zombies.forEach((otherZombie) => {
                if (otherZombie !== zombie) {
                  const chainDist = Math.sqrt(
                    Math.pow(otherZombie.x - zombie.x, 2) + 
                    Math.pow(otherZombie.y - zombie.y, 2)
                  );
                  if (chainDist < chainRange) {
                    otherZombie.health -= bullet.damage * 0.5;
                    createParticles(otherZombie.x, otherZombie.y, '#00ffff', 8);
                  }
                }
              });
            }
            
            if (bullet.fromTurret) {
              gameRef.current.stats.turretKills += 0.1;
            }
            
            if (bullet.explosive) {
              createExplosion(bullet.x, bullet.y, 50, bullet.damage * 0.5);
              game.bullets.splice(bulletIndex, 1);
            } else if (bullet.piercing < 0 && bullet.ricochet <= 0) {
              game.bullets.splice(bulletIndex, 1);
            }
            
                          if (zombie.health <= 0) {
              setScore(s => s + zombie.score);
              gameRef.current.stats.zombiesKilled++;
              
              // Kill streak system
              setKillStreak(k => {
                const newStreak = k + 1;
                setMaxKillStreak(max => Math.max(max, newStreak));
                
                // Bonus coins for streaks
                if (newStreak % 10 === 0) {
                  setCoins(c => c + 10);
                  createParticles(zombie.x, zombie.y, '#ffd700', 25);
                }
                
                return newStreak;
              });
              
              // Reset streak timer
              setTimeout(() => setKillStreak(0), 3000);
              
              // Screen shake on boss kill
              if (zombie.type === 'boss' || zombie.type === 'megaboss') {
                addScreenShake(zombie.type === 'megaboss' ? 15 : 10);
              }
              
              // Special zombie death effects
              if (zombie.type === 'healer') {
                createParticles(zombie.x, zombie.y, '#2ecc71', 15);
              } else if (zombie.type === 'splitter') {
                // Spawn 2 smaller zombies
                for (let i = 0; i < zombie.splits; i++) {
                  const angle = (i / zombie.splits) * Math.PI * 2;
                  game.zombies.push({
                    ...zombieTypes.fast,
                    type: 'fast',
                    x: zombie.x + Math.cos(angle) * 30,
                    y: zombie.y + Math.sin(angle) * 30,
                    health: 1,
                    maxHealth: 1,
                    baseSpeed: 2,
                    targetLock: zombie.targetLock,
                    preferPlayer: zombie.preferPlayer
                  });
                }
                createParticles(zombie.x, zombie.y, '#e67e22', 20);
              } else if (zombie.type === 'necromancer') {
                createParticles(zombie.x, zombie.y, '#9b59b6', 30);
                addScreenShake(8);
              }
              
              // Random power-up drops (10% chance)
              if (Math.random() < 0.1) {
                const powerUpTypes = ['health', 'speed', 'damage', 'firerate', 'coins'];
                const powerUpType = powerUpTypes[Math.floor(Math.random() * powerUpTypes.length)];
                game.powerUps.push({
                  type: powerUpType,
                  x: zombie.x,
                  y: zombie.y,
                  lifetime: 600,
                  collected: false
                });
              }
              
              // Bloodlust: speed boost on kill
              if (game.player.bloodlust) {
                game.player.bloodlustStacks = Math.min(10, (game.player.bloodlustStacks || 0) + 1);
                setTimeout(() => {
                  game.player.bloodlustStacks = Math.max(0, game.player.bloodlustStacks - 1);
                }, 3000);
              }
              
              setXp(x => {
                const xpBoost = game.player.xpBoost || 1; // Default to 1 if undefined
                const xpGained = zombie.xp * xpBoost;
                const newXp = x + xpGained;
                const xpNeeded = getXpForLevel(level);
                
                console.log(`💎 XP: ${Math.floor(newXp)}/${xpNeeded} (gained ${Math.floor(xpGained)})`);
                
                if (newXp >= xpNeeded) {
                  let levelsGained = 0;
                  let remainingXp = newXp;
                  let currentLevel = level;
                  
                  // Calculate how many levels gained
                  while (remainingXp >= getXpForLevel(currentLevel)) {
                    remainingXp -= getXpForLevel(currentLevel);
                    currentLevel++;
                    levelsGained++;
                  }
                  
                  console.log(`🎉 LEVEL UP! Gained ${levelsGained} level(s)! Now level ${currentLevel}`);
                  
                  setLevel(l => l + levelsGained);
                  setPendingLevelUps(prev => prev + levelsGained);
                  
                  // Only show level up screen if not already showing
                  if (!showLevelUp) {
                    setTotalLevelUps(levelsGained);
                    setCurrentUpgradeOptions(getRandomUpgrades());
                    setShowLevelUp(true);
                    game.isPaused = true;
                  } else {
                    // If already showing, add to the total
                    setTotalLevelUps(prev => prev + levelsGained);
                  }
                  
                  return remainingXp;
                }
                return newXp;
              });
              
              // Lifesteal
              const totalLifesteal = (game.player.lifeSteal || 0) + (game.player.vampire ? 0.1 : 0);
              if (totalLifesteal > 0) {
                game.player.health = Math.min(
                  game.player.maxHealth,
                  game.player.health + game.player.maxHealth * totalLifesteal
                );
              }
              
              createParticles(zombie.x, zombie.y, zombie.color, 10);
              
              // XP gain visual feedback
              createParticles(zombie.x, zombie.y, '#9b59b6', 5);
              game.particles.push({
                x: zombie.x,
                y: zombie.y - 20,
                vx: 0,
                vy: -2,
                size: 12,
                color: '#9b59b6',
                life: 60,
                alpha: 1,
                rotation: 0,
                rotationSpeed: 0,
                isText: true,
                text: `+${zombie.xp}XP`
              });
              
              // Coin drops with Scavenger and Lucky modifiers
              let coinValue = zombie.coins;
              if (game.player.scavenger) {
                coinValue = Math.floor(coinValue * 1.5);
              }
              if (game.player.lucky && Math.random() < 0.15) {
                coinValue *= 2;
                createParticles(zombie.x, zombie.y, '#ffd700', 15);
              }
              
              game.coinDrops.push({
                x: zombie.x,
                y: zombie.y,
                value: coinValue,
                lifetime: 300
              });
              
              if (zombie.type === 'exploder') {
                createExplosion(zombie.x, zombie.y, 80, 2);
              }
              
              game.zombies.splice(zombieIndex, 1);
            }
          }
        });
      });

      // Wave completion
      if (game.zombies.length === 0 && game.zombiesLeftToSpawn === 0 && game.waveActive) {
        console.log(`✅ Wave ${wave} completed!`);
        game.waveActive = false;
        const nextWave = wave + 1;
        setWave(nextWave);
        game.player.health = Math.min(game.player.maxHealth, game.player.health + 30);
        
        const waveBonus = Math.max(5, 10 + (wave * 2)); // Reduced bonus, min 5
        setCoins(c => c + waveBonus);
        gameRef.current.stats.coinsEarned += waveBonus;
        
        // Schedule next wave
        game.nextWaveTime = Date.now() + 10000;
        console.log(`⏳ Next wave (${nextWave}) starts in 10s...`);
        
        // Use a more reliable trigger
        const waveTimer = setTimeout(() => {
          console.log(`🌊 Starting wave ${nextWave}...`);
          if (gameState === 'playing' && !game.isPaused && game.bases.length > 0) {
            game.nextWaveTime = null;
            startWave(nextWave);
          } else {
            console.log('❌ Wave start cancelled - game not playing or no base');
          }
        }, 10000);
        
        // Store timer ID for cleanup if needed
        game.nextWaveTimer = waveTimer;
      }
      
      // Failsafe: Auto-start wave if stuck (no zombies, no active wave, base exists, playing)
      // Wait at least 15 seconds after game start or last wave before failsafe triggers
      // Don't trigger during initial countdown
      const timeSinceLastWave = game.nextWaveTime ? (Date.now() - (game.nextWaveTime - 10000)) : Date.now();
      if (game.zombies.length === 0 && 
          game.zombiesLeftToSpawn === 0 && 
          !game.waveActive && 
          game.bases.length > 0 && 
          gameState === 'playing' && 
          !game.isPaused &&
          !game.nextWaveTime &&
          !game.initialCountdownActive &&
          waveCountdown === 0 &&
          timeSinceLastWave > 15000) {
        console.log('⚠️ FAILSAFE: No wave active for 15+ seconds, auto-starting wave', wave);
        startWave(wave);
      }

      // Particles
      game.particles = game.particles.filter(p => {
        p.x += p.vx;
        p.y += p.vy;
        p.vx *= 0.95;
        p.vy *= 0.95;
        p.life--;
        return p.life > 0;
      });

      if (game.rotationFlash > 0) {
        game.rotationFlash--;
      }

      // === RENDERING ===
      
      // Grid - much more subtle
      ctx.strokeStyle = selectedBuild ? 'rgba(78, 204, 163, 0.08)' : 'rgba(100, 120, 150, 0.03)';
      ctx.lineWidth = 1;
      for (let x = 0; x < game.mapWidth; x += 50) {
        const screenX = x - game.cameraX;
        if (screenX > -50 && screenX < canvas.width + 50) {
          ctx.beginPath();
          ctx.moveTo(screenX, 0);
          ctx.lineTo(screenX, canvas.height);
          ctx.stroke();
        }
      }
      for (let y = 0; y < game.mapHeight; y += 50) {
        const screenY = y - game.cameraY;
        if (screenY > -50 && screenY < canvas.height + 50) {
          ctx.beginPath();
          ctx.moveTo(0, screenY);
          ctx.lineTo(canvas.width, screenY);
          ctx.stroke();
        }
      }

      // Obstacles
      game.obstacles.forEach(obs => {
        const screenX = obs.x - game.cameraX;
        const screenY = obs.y - game.cameraY;
        if (screenX + obs.width > 0 && screenX < canvas.width && screenY + obs.height > 0 && screenY < canvas.height) {
          ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
          ctx.fillRect(screenX + 5, screenY + 5, obs.width, obs.height);
          
          ctx.fillStyle = obs.isWall ? '#34495e' : '#4a5568';
          ctx.fillRect(screenX, screenY, obs.width, obs.height);
          
          ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
          ctx.fillRect(screenX, screenY, obs.width, 3);
          
          ctx.strokeStyle = '#1a202c';
          ctx.lineWidth = 2;
          ctx.strokeRect(screenX, screenY, obs.width, obs.height);
        }
      });

      // Walls with enhanced 3D rendering
      game.walls.forEach(wall => {
        const screenX = wall.x - game.cameraX;
        const screenY = wall.y - game.cameraY;
        
        // Enhanced shadow with blur
        ctx.shadowBlur = 15;
        ctx.shadowColor = 'rgba(0, 0, 0, 0.6)';
        ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
        ctx.fillRect(screenX + 5, screenY + 5, wall.width, wall.height);
        ctx.shadowBlur = 0;
        
        // Base wall with tier-specific textures
        let wallTexture;
        if (wall.tier === 1) {
          // Wood texture
          wallTexture = ctx.createLinearGradient(screenX, screenY, screenX + wall.width, screenY + wall.height);
          wallTexture.addColorStop(0, '#8B4513');
          wallTexture.addColorStop(0.5, '#A0522D');
          wallTexture.addColorStop(1, '#6B3410');
          ctx.fillStyle = wallTexture;
          ctx.fillRect(screenX, screenY, wall.width, wall.height);
          
          // Wood grain
          ctx.strokeStyle = 'rgba(101, 67, 33, 0.5)';
          ctx.lineWidth = 2;
          for (let i = 0; i < wall.height; i += 8) {
            ctx.beginPath();
            ctx.moveTo(screenX, screenY + i);
            ctx.lineTo(screenX + wall.width, screenY + i);
            ctx.stroke();
          }
          
          // Wood planks
          for (let i = 0; i < (wall.height > wall.width ? wall.height : wall.width); i += 20) {
            ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)';
            ctx.lineWidth = 3;
            if (wall.height > wall.width) {
              ctx.beginPath();
              ctx.moveTo(screenX, screenY + i);
              ctx.lineTo(screenX + wall.width, screenY + i);
              ctx.stroke();
            } else {
              ctx.beginPath();
              ctx.moveTo(screenX + i, screenY);
              ctx.lineTo(screenX + i, screenY + wall.height);
              ctx.stroke();
            }
          }
        } else if (wall.tier === 2) {
          // Stone texture
          wallTexture = ctx.createLinearGradient(screenX, screenY, screenX + wall.width, screenY + wall.height);
          wallTexture.addColorStop(0, '#708090');
          wallTexture.addColorStop(0.5, '#556B7D');
          wallTexture.addColorStop(1, '#4A5660');
          ctx.fillStyle = wallTexture;
          ctx.fillRect(screenX, screenY, wall.width, wall.height);
          
          // Stone blocks
          const blockSize = 25;
          for (let by = 0; by < wall.height; by += blockSize) {
            for (let bx = 0; bx < wall.width; bx += blockSize) {
              ctx.strokeStyle = 'rgba(0, 0, 0, 0.4)';
              ctx.lineWidth = 2;
              ctx.strokeRect(screenX + bx, screenY + by, Math.min(blockSize, wall.width - bx), Math.min(blockSize, wall.height - by));
              
              // Stone texture detail
              for (let i = 0; i < 3; i++) {
                ctx.fillStyle = `rgba(${100 + Math.random() * 50}, ${110 + Math.random() * 50}, ${120 + Math.random() * 50}, 0.3)`;
                ctx.fillRect(
                  screenX + bx + Math.random() * blockSize,
                  screenY + by + Math.random() * blockSize,
                  2, 2
                );
              }
            }
          }
        } else if (wall.tier === 3) {
          // Metal texture
          wallTexture = ctx.createLinearGradient(screenX, screenY, screenX + wall.width, screenY + wall.height);
          wallTexture.addColorStop(0, '#B0C4DE');
          wallTexture.addColorStop(0.3, '#708090');
          wallTexture.addColorStop(0.7, '#4F6D7A');
          wallTexture.addColorStop(1, '#2F4F5F');
          ctx.fillStyle = wallTexture;
          ctx.fillRect(screenX, screenY, wall.width, wall.height);
          
          // Metal panels
          const panelSize = 30;
          for (let py = 0; py < wall.height; py += panelSize) {
            for (let px = 0; px < wall.width; px += panelSize) {
              // Panel outline
              ctx.strokeStyle = '#1C1C1C';
              ctx.lineWidth = 2;
              ctx.strokeRect(screenX + px, screenY + py, Math.min(panelSize, wall.width - px), Math.min(panelSize, wall.height - py));
              
              // Rivets
              ctx.fillStyle = '#FFD700';
              const rivetPositions = [[2, 2], [panelSize-4, 2], [2, panelSize-4], [panelSize-4, panelSize-4]];
              rivetPositions.forEach(([rx, ry]) => {
                if (px + rx < wall.width && py + ry < wall.height) {
                  ctx.beginPath();
                  ctx.arc(screenX + px + rx, screenY + py + ry, 2, 0, Math.PI * 2);
                  ctx.fill();
                }
              });
              
              // Metallic shine
              ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
              ctx.fillRect(screenX + px + 2, screenY + py + 2, Math.min(panelSize - 4, wall.width - px - 4), 4);
            }
          }
          
          // Warning stripes
          ctx.strokeStyle = '#FFD700';
          ctx.lineWidth = 3;
          ctx.setLineDash([10, 10]);
          ctx.strokeRect(screenX + 2, screenY + 2, wall.width - 4, wall.height - 4);
          ctx.setLineDash([]);
        }
        
        // Top highlight for 3D effect
        const highlightGradient = ctx.createLinearGradient(screenX, screenY, screenX, screenY + 10);
        highlightGradient.addColorStop(0, 'rgba(255, 255, 255, 0.4)');
        highlightGradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
        ctx.fillStyle = highlightGradient;
        ctx.fillRect(screenX, screenY, wall.width, 10);
        
        // Side edge for depth
        ctx.fillStyle = darkenColor(wall.color || '#95a5a6', 40);
        ctx.fillRect(screenX + wall.width - 4, screenY, 4, wall.height);
        
        // Armor glow effect
        if (wall.armor > 0) {
          ctx.shadowBlur = 10;
          ctx.shadowColor = 'rgba(255, 215, 0, 0.5)';
          ctx.strokeStyle = 'rgba(255, 215, 0, 0.4)';
          ctx.lineWidth = 3;
          ctx.strokeRect(screenX + 2, screenY + 2, wall.width - 4, wall.height - 4);
          ctx.shadowBlur = 0;
        }
        
        // Main border - thick and prominent
        ctx.strokeStyle = darkenColor(wall.color || '#95a5a6', 50);
        ctx.lineWidth = 4;
        ctx.strokeRect(screenX, screenY, wall.width, wall.height);
        
        // Outer glow border
        ctx.strokeStyle = lightenColor(wall.color || '#95a5a6', 30);
        ctx.lineWidth = 2;
        ctx.strokeRect(screenX - 1, screenY - 1, wall.width + 2, wall.height + 2);
        
        // Selection highlight
        if (selectedStructure && selectedStructure.type === 'wall' && selectedStructure.data === wall) {
          ctx.shadowBlur = 20;
          ctx.shadowColor = '#ffff00';
          ctx.strokeStyle = '#ffff00';
          ctx.lineWidth = 5;
          ctx.strokeRect(screenX - 3, screenY - 3, wall.width + 6, wall.height + 6);
          ctx.shadowBlur = 0;
          
          ctx.fillStyle = 'rgba(255, 255, 0, 0.15)';
          ctx.fillRect(screenX, screenY, wall.width, wall.height);
        }
        
        // Icon with better rendering
        ctx.font = 'bold 32px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.shadowBlur = 5;
        ctx.shadowColor = 'rgba(0, 0, 0, 0.8)';
        const wallIcon = wall.icon || (wall.tier === 1 ? '🪵' : wall.tier === 2 ? '🧱' : wall.tier === 3 ? '🔩' : '🧱');
        ctx.fillText(wallIcon, screenX + wall.width/2, screenY + wall.height/2);
        ctx.shadowBlur = 0;
        
        // Upgrade stars with glow
        if (wall.upgradeLevel > 0) {
          ctx.font = 'bold 12px Arial';
          ctx.textAlign = 'right';
          ctx.shadowBlur = 5;
          ctx.shadowColor = '#ffd700';
          ctx.fillStyle = '#ffd700';
          ctx.strokeStyle = '#000';
          ctx.lineWidth = 3;
          const starText = '★'.repeat(Math.min(wall.upgradeLevel, 5));
          ctx.strokeText(starText, screenX + wall.width - 6, screenY + 14);
          ctx.fillText(starText, screenX + wall.width - 6, screenY + 14);
          ctx.shadowBlur = 0;
        }
        
        // Enhanced health bar
        const barWidth = Math.max(wall.width, wall.height);
        const barHeight = 6;
        const barX = screenX;
        const barY = screenY - 12;
        
        // Health bar shadow
        ctx.shadowBlur = 5;
        ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(barX - 2, barY - 2, barWidth + 4, barHeight + 4);
        ctx.shadowBlur = 0;
        
        // Health bar background
        ctx.fillStyle = '#2c3e50';
        ctx.fillRect(barX, barY, barWidth, barHeight);
        
        // Health bar fill with gradient
        const healthPercent = wall.health / wall.maxHealth;
        const healthGradient = ctx.createLinearGradient(barX, barY, barX + barWidth, barY);
        if (healthPercent > 0.6) {
          healthGradient.addColorStop(0, '#27ae60');
          healthGradient.addColorStop(1, '#2ecc71');
        } else if (healthPercent > 0.3) {
          healthGradient.addColorStop(0, '#f39c12');
          healthGradient.addColorStop(1, '#e67e22');
        } else {
          healthGradient.addColorStop(0, '#c0392b');
          healthGradient.addColorStop(1, '#e74c3c');
        }
        ctx.fillStyle = healthGradient;
        ctx.fillRect(barX, barY, barWidth * healthPercent, barHeight);
        
        // Health bar border
        ctx.strokeStyle = '#ecf0f1';
        ctx.lineWidth = 2;
        ctx.strokeRect(barX, barY, barWidth, barHeight);
      });

      // Turrets with enhanced 3D rendering
      game.turrets.forEach(turret => {
        const turretSize = turret.size || 50;
        const centerX = turret.x + turretSize / 2;
        const centerY = turret.y + turretSize / 2;
        const screenX = turret.x - game.cameraX;
        const screenY = turret.y - game.cameraY;
        const screenCenterX = centerX - game.cameraX;
        const screenCenterY = centerY - game.cameraY;
        
        const turretColor = turret.color || '#3498db';
        
        // Range indicator with gradient - only show if Q is pressed
        if (showRanges) {
          const rangeGradient = ctx.createRadialGradient(screenCenterX, screenCenterY, 0, screenCenterX, screenCenterY, turret.range);
          rangeGradient.addColorStop(0, turretColor + '40');
          rangeGradient.addColorStop(0.7, turretColor + '20');
          rangeGradient.addColorStop(1, turretColor + '00');
          ctx.fillStyle = rangeGradient;
          ctx.beginPath();
          ctx.arc(screenCenterX, screenCenterY, turret.range, 0, Math.PI * 2);
          ctx.fill();
          
          ctx.strokeStyle = turretColor + '40';
          ctx.lineWidth = 2;
          ctx.setLineDash([5, 5]);
          ctx.beginPath();
          ctx.arc(screenCenterX, screenCenterY, turret.range, 0, Math.PI * 2);
          ctx.stroke();
          ctx.setLineDash([]);
        }
        
        // Enhanced shadow
        ctx.shadowBlur = 20;
        ctx.shadowColor = 'rgba(0, 0, 0, 0.6)';
        ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
        ctx.fillRect(screenX + 5, screenY + 5, turretSize, turretSize);
        ctx.shadowBlur = 0;
        
        // Base platform with 3D effect
        const baseGradient = ctx.createLinearGradient(screenX, screenY, screenX, screenY + turretSize);
        baseGradient.addColorStop(0, '#4a4a4a');
        baseGradient.addColorStop(0.5, '#2c2c2c');
        baseGradient.addColorStop(1, '#1a1a1a');
        ctx.fillStyle = baseGradient;
        ctx.fillRect(screenX, screenY, turretSize, turretSize);
        
        // Metallic border
        ctx.strokeStyle = '#6a6a6a';
        ctx.lineWidth = 2;
        ctx.strokeRect(screenX, screenY, turretSize, turretSize);
        
        // Turret base - circular platform
        const platformGrad = ctx.createRadialGradient(screenCenterX, screenCenterY, 0, screenCenterX, screenCenterY, turretSize/2);
        platformGrad.addColorStop(0, lightenColor(turretColor, 30));
        platformGrad.addColorStop(0.6, turretColor);
        platformGrad.addColorStop(1, darkenColor(turretColor, 40));
        ctx.fillStyle = platformGrad;
        ctx.beginPath();
        ctx.arc(screenCenterX, screenCenterY, turretSize * 0.4, 0, Math.PI * 2);
        ctx.fill();
        
        // Find target for barrel rotation
        let targetAngle = 0;
        let closestZombie = null;
        let closestDist = turret.range;
        
        game.zombies.forEach(zombie => {
          const dist = Math.sqrt(
            Math.pow(zombie.x - centerX, 2) + 
            Math.pow(zombie.y - centerY, 2)
          );
          
          if (dist < closestDist) {
            closestDist = dist;
            closestZombie = zombie;
          }
        });
        
        if (closestZombie) {
          targetAngle = Math.atan2(closestZombie.y - centerY, closestZombie.x - centerX);
        }
        
        // Turret type-specific designs
        if (turret.turretType === 'turret_sniper') {
          // Sniper - long barrel
          ctx.save();
          ctx.translate(screenCenterX, screenCenterY);
          ctx.rotate(targetAngle);
          
          // Base mount
          ctx.fillStyle = darkenColor(turretColor, 20);
          ctx.fillRect(-8, -8, 16, 16);
          
          // Long barrel with scope
          ctx.fillStyle = '#2c3e50';
          ctx.fillRect(0, -4, 30, 8);
          
          // Scope
          ctx.fillStyle = '#1a252f';
          ctx.fillRect(15, -6, 8, 12);
          
          // Muzzle
          ctx.fillStyle = '#95a5a6';
          ctx.fillRect(28, -3, 4, 6);
          
          // Laser sight
          ctx.strokeStyle = 'rgba(255, 0, 0, 0.3)';
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(30, 0);
          ctx.lineTo(150, 0);
          ctx.stroke();
          
          ctx.restore();
        } else if (turret.turretType === 'turret_rapid') {
          // Rapid - multiple barrels
          ctx.save();
          ctx.translate(screenCenterX, screenCenterY);
          ctx.rotate(targetAngle);
          
          // Rotating barrel assembly
          const barrelSpin = (Date.now() / 50) % (Math.PI * 2);
          
          for (let i = 0; i < 6; i++) {
            const angle = (i / 6) * Math.PI * 2 + barrelSpin;
            const bx = Math.cos(angle) * 6;
            const by = Math.sin(angle) * 6;
            
            ctx.fillStyle = '#2c3e50';
            ctx.fillRect(bx - 2, by - 2, 18, 4);
            
            ctx.fillStyle = '#1a252f';
            ctx.fillRect(bx + 14, by - 1, 3, 2);
          }
          
          // Center hub
          ctx.fillStyle = darkenColor(turretColor, 30);
          ctx.beginPath();
          ctx.arc(0, 0, 8, 0, Math.PI * 2);
          ctx.fill();
          
          ctx.restore();
        } else if (turret.turretType === 'turret_bomber') {
          // Bomber - chunky launcher
          ctx.save();
          ctx.translate(screenCenterX, screenCenterY);
          ctx.rotate(targetAngle);
          
          // Missile pod
          ctx.fillStyle = darkenColor(turretColor, 20);
          ctx.fillRect(-10, -12, 30, 24);
          
          // Missile tubes
          for (let i = 0; i < 3; i++) {
            ctx.fillStyle = '#1a1a1a';
            ctx.fillRect(8, -10 + i * 8, 12, 6);
            
            // Missile tip
            ctx.fillStyle = '#ff6b6b';
            ctx.beginPath();
            ctx.moveTo(20, -7 + i * 8);
            ctx.lineTo(23, -4 + i * 8);
            ctx.lineTo(20, -1 + i * 8);
            ctx.fill();
          }
          
          // Warning stripes
          ctx.strokeStyle = '#ffff00';
          ctx.lineWidth = 2;
          for (let i = 0; i < 4; i++) {
            ctx.beginPath();
            ctx.moveTo(-8 + i * 4, -12);
            ctx.lineTo(-6 + i * 4, 12);
            ctx.stroke();
          }
          
          ctx.restore();
        } else if (turret.turretType === 'turret_freeze') {
          // Freeze - crystalline design
          ctx.save();
          ctx.translate(screenCenterX, screenCenterY);
          ctx.rotate(targetAngle);
          
          // Ice crystal base
          ctx.fillStyle = 'rgba(0, 200, 255, 0.7)';
          ctx.beginPath();
          for (let i = 0; i < 6; i++) {
            const angle = (i / 6) * Math.PI * 2;
            const radius = i % 2 === 0 ? 12 : 8;
            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * radius;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
          }
          ctx.closePath();
          ctx.fill();
          
          // Freeze ray emitter
          ctx.fillStyle = '#00ffff';
          ctx.fillRect(0, -6, 20, 12);
          
          // Beam effect
          if (closestZombie && closestDist < turret.range) {
            ctx.strokeStyle = 'rgba(0, 255, 255, 0.5)';
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(18, 0);
            ctx.lineTo(turret.range, 0);
            ctx.stroke();
          }
          
          ctx.restore();
        } else {
          // Basic turret - standard gun
          ctx.save();
          ctx.translate(screenCenterX, screenCenterY);
          ctx.rotate(targetAngle);
          
          // Gun mount
          ctx.fillStyle = darkenColor(turretColor, 20);
          ctx.fillRect(-6, -6, 12, 12);
          
          // Barrel
          ctx.fillStyle = '#2c3e50';
          ctx.fillRect(0, -4, 22, 8);
          
          // Barrel detail
          ctx.fillStyle = '#1a252f';
          ctx.fillRect(18, -3, 5, 6);
          
          // Muzzle
          ctx.fillStyle = lightenColor(turretColor, 30);
          ctx.fillRect(20, -2, 3, 4);
          
          ctx.restore();
        }
        
        // Muzzle flash effect for all turrets
        if (turret.lastShotTime && Date.now() - turret.lastShotTime < 100) {
          ctx.save();
          ctx.translate(screenCenterX, screenCenterY);
          ctx.rotate(targetAngle);
          
          ctx.shadowBlur = 25;
          ctx.shadowColor = '#ffff00';
          ctx.fillStyle = '#ffff00';
          ctx.beginPath();
          ctx.arc(24, 0, 8, 0, Math.PI * 2);
          ctx.fill();
          
          // Flash rays
          for (let i = 0; i < 6; i++) {
            const rayAngle = (i / 6) * Math.PI * 2;
            ctx.beginPath();
            ctx.moveTo(24, 0);
            ctx.lineTo(24 + Math.cos(rayAngle) * 12, Math.sin(rayAngle) * 12);
            ctx.strokeStyle = '#ffaa00';
            ctx.lineWidth = 2;
            ctx.stroke();
          }
          ctx.shadowBlur = 0;
          ctx.restore();
        }
        
        // Outer border with multiple layers
        ctx.strokeStyle = '#1a1a1a';
        ctx.lineWidth = 3;
        ctx.strokeRect(screenX, screenY, turretSize, turretSize);
        
        ctx.strokeStyle = lightenColor(turretColor, 40);
        ctx.lineWidth = 1;
        ctx.strokeRect(screenX - 1, screenY - 1, turretSize + 2, turretSize + 2);
        
        // Selection highlight
        if (selectedStructure && selectedStructure.type === 'turret' && selectedStructure.data === turret) {
          ctx.shadowBlur = 25;
          ctx.shadowColor = '#00ff00';
          ctx.strokeStyle = '#00ff00';
          ctx.lineWidth = 5;
          ctx.strokeRect(screenX - 3, screenY - 3, turretSize + 6, turretSize + 6);
          ctx.shadowBlur = 0;
          
          ctx.fillStyle = 'rgba(0, 255, 0, 0.15)';
          ctx.fillRect(screenX, screenY, turretSize, turretSize);
        }
        
        // Upgrade stars with glow
        if (turret.upgradeLevel > 0) {
          ctx.shadowBlur = 8;
          ctx.shadowColor = '#ffd700';
          ctx.fillStyle = '#ffd700';
          ctx.font = 'bold 14px Arial';
          ctx.textAlign = 'right';
          ctx.strokeStyle = '#000';
          ctx.lineWidth = 3;
          const starText = '★' + turret.upgradeLevel;
          ctx.strokeText(starText, screenX + turretSize - 4, screenY + 16);
          ctx.fillText(starText, screenX + turretSize - 4, screenY + 16);
          ctx.shadowBlur = 0;
        }
        
        // Enhanced health bar
        const barWidth = turretSize;
        const barHeight = 6;
        const barX = screenX;
        const barY = screenY - 12;
        
        // Health bar shadow
        ctx.shadowBlur = 5;
        ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(barX - 2, barY - 2, barWidth + 4, barHeight + 4);
        ctx.shadowBlur = 0;
        
        // Health bar background
        ctx.fillStyle = '#2c3e50';
        ctx.fillRect(barX, barY, barWidth, barHeight);
        
        // Health bar fill with gradient
        const healthPercent = turret.health / turret.maxHealth;
        const healthGradient = ctx.createLinearGradient(barX, barY, barX + barWidth, barY);
        if (healthPercent > 0.6) {
          healthGradient.addColorStop(0, '#27ae60');
          healthGradient.addColorStop(1, '#2ecc71');
        } else if (healthPercent > 0.3) {
          healthGradient.addColorStop(0, '#f39c12');
          healthGradient.addColorStop(1, '#e67e22');
        } else {
          healthGradient.addColorStop(0, '#c0392b');
          healthGradient.addColorStop(1, '#e74c3c');
        }
        ctx.fillStyle = healthGradient;
        ctx.fillRect(barX, barY, barWidth * healthPercent, barHeight);
        
        // Health bar shine
        ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
        ctx.fillRect(barX, barY, barWidth * healthPercent, 2);
        
        // Health bar border
        ctx.strokeStyle = '#ecf0f1';
        ctx.lineWidth = 2;
        ctx.strokeRect(barX, barY, barWidth, barHeight);
      });

      // Traps
      game.traps.forEach(trap => {
        const screenX = trap.x - game.cameraX;
        const screenY = trap.y - game.cameraY;
        
        ctx.fillStyle = 'rgba(192, 57, 43, 0.3)';
        ctx.beginPath();
        ctx.arc(screenX, screenY, 25, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.strokeStyle = '#c0392b';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(screenX, screenY, 25, 0, Math.PI * 2);
        ctx.stroke();
        
        ctx.font = 'bold 24px Arial';
        ctx.textAlign = 'center';
        ctx.fillStyle = '#e74c3c';
        ctx.fillText('⚠️', screenX, screenY + 8);
      });

      // Bases with enhanced rendering
      game.bases.forEach(base => {
        const screenX = base.x - game.cameraX;
        const screenY = base.y - game.cameraY;
        
        // Safe zone indicator (no spawn zone) - only show if Q is pressed
        if (showRanges) {
          const pulseScale = 1 + Math.sin(Date.now() / 1000) * 0.02;
          ctx.strokeStyle = 'rgba(0, 255, 150, 0.2)';
          ctx.lineWidth = 3;
          ctx.setLineDash([15, 15]);
          ctx.beginPath();
          ctx.arc(screenX + base.size/2, screenY + base.size/2, 400 * pulseScale, 0, Math.PI * 2);
          ctx.stroke();
          ctx.setLineDash([]);
          
          // Fill safe zone with subtle color
          ctx.fillStyle = 'rgba(0, 255, 150, 0.03)';
          ctx.beginPath();
          ctx.arc(screenX + base.size/2, screenY + base.size/2, 400, 0, Math.PI * 2);
          ctx.fill();
          
          // Safe zone label
          ctx.font = 'bold 14px Arial';
          ctx.textAlign = 'center';
          ctx.fillStyle = 'rgba(0, 255, 150, 0.6)';
          ctx.strokeStyle = 'rgba(0, 0, 0, 0.8)';
          ctx.lineWidth = 3;
          ctx.strokeText('🛡️ SAFE ZONE', screenX + base.size/2, screenY + base.size/2 - 220);
          ctx.fillText('🛡️ SAFE ZONE', screenX + base.size/2, screenY + base.size/2 - 220);
          ctx.font = 'bold 10px Arial';
          ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
          ctx.strokeText('Zombies cannot spawn here', screenX + base.size/2, screenY + base.size/2 - 205);
          ctx.fillText('Zombies cannot spawn here', screenX + base.size/2, screenY + base.size/2 - 205);
        }
        
        // Pulsing glow effect
        const pulseIntensity = 0.7 + Math.sin(Date.now() / 500) * 0.3;
        
        // Large outer glow
        ctx.shadowBlur = 40 * pulseIntensity;
        ctx.shadowColor = '#f39c12';
        
        // Base platform shadow
        ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        ctx.fillRect(screenX + 8, screenY + 8, base.size, base.size);
        
        // Base gradient background
        const baseGradient = ctx.createRadialGradient(
          screenX + base.size/2, screenY + base.size/2, 0,
          screenX + base.size/2, screenY + base.size/2, base.size
        );
        baseGradient.addColorStop(0, '#f39c12');
        baseGradient.addColorStop(0.7, '#e67e22');
        baseGradient.addColorStop(1, '#d35400');
        ctx.fillStyle = baseGradient;
        ctx.fillRect(screenX, screenY, base.size, base.size);
        
        // Top highlight shine
        const shineGradient = ctx.createLinearGradient(screenX, screenY, screenX, screenY + base.size/3);
        shineGradient.addColorStop(0, 'rgba(255, 255, 255, 0.4)');
        shineGradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
        ctx.fillStyle = shineGradient;
        ctx.fillRect(screenX, screenY, base.size, base.size/3);
        
        // Armor plating effect
        if (base.armor > 0) {
          for (let i = 0; i < base.armor; i++) {
            ctx.strokeStyle = `rgba(255, 215, 0, ${0.3 + i * 0.1})`;
            ctx.lineWidth = 3;
            ctx.strokeRect(screenX + 3 + i * 2, screenY + 3 + i * 2, base.size - 6 - i * 4, base.size - 6 - i * 4);
          }
        }
        
        // Main border
        ctx.strokeStyle = '#c0392b';
        ctx.lineWidth = 5;
        ctx.strokeRect(screenX, screenY, base.size, base.size);
        
        // Outer glow border
        ctx.shadowBlur = 20 * pulseIntensity;
        ctx.strokeStyle = '#f39c12';
        ctx.lineWidth = 3;
        ctx.strokeRect(screenX - 2, screenY - 2, base.size + 4, base.size + 4);
        
        ctx.shadowBlur = 0;
        
        // Base icon - enhanced 3D fortress rendering
        
        // Fortress structure layers
        // Bottom layer - foundation
        ctx.fillStyle = '#5a4a3a';
        ctx.fillRect(screenX + base.size * 0.1, screenY + base.size * 0.7, base.size * 0.8, base.size * 0.25);
        
        // Middle layer - main structure
        const structureGrad = ctx.createLinearGradient(
          screenX + base.size * 0.2, screenY + base.size * 0.3,
          screenX + base.size * 0.8, screenY + base.size * 0.7
        );
        structureGrad.addColorStop(0, '#d4a574');
        structureGrad.addColorStop(0.5, '#c19a6b');
        structureGrad.addColorStop(1, '#8b7355');
        ctx.fillStyle = structureGrad;
        ctx.fillRect(screenX + base.size * 0.15, screenY + base.size * 0.3, base.size * 0.7, base.size * 0.4);
        
        // Windows
        ctx.fillStyle = '#87ceeb';
        ctx.shadowBlur = 5;
        ctx.shadowColor = '#87ceeb';
        for (let i = 0; i < 3; i++) {
          ctx.fillRect(
            screenX + base.size * 0.25 + i * base.size * 0.2,
            screenY + base.size * 0.4,
            base.size * 0.12,
            base.size * 0.15
          );
        }
        ctx.shadowBlur = 0;
        
        // Roof
        ctx.fillStyle = '#8b0000';
        ctx.beginPath();
        ctx.moveTo(screenX + base.size * 0.1, screenY + base.size * 0.3);
        ctx.lineTo(screenX + base.size * 0.5, screenY + base.size * 0.15);
        ctx.lineTo(screenX + base.size * 0.9, screenY + base.size * 0.3);
        ctx.closePath();
        ctx.fill();
        
        // Roof highlight
        ctx.fillStyle = 'rgba(255, 100, 100, 0.4)';
        ctx.beginPath();
        ctx.moveTo(screenX + base.size * 0.1, screenY + base.size * 0.3);
        ctx.lineTo(screenX + base.size * 0.5, screenY + base.size * 0.15);
        ctx.lineTo(screenX + base.size * 0.5, screenY + base.size * 0.25);
        ctx.closePath();
        ctx.fill();
        
        // Antenna/tower
        ctx.strokeStyle = '#708090';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(screenX + base.size * 0.5, screenY + base.size * 0.15);
        ctx.lineTo(screenX + base.size * 0.5, screenY + base.size * 0.05);
        ctx.stroke();
        
        // Antenna light
        const antennaLight = Math.sin(Date.now() / 300) * 0.5 + 0.5;
        ctx.fillStyle = `rgba(255, 0, 0, ${antennaLight})`;
        ctx.shadowBlur = 10;
        ctx.shadowColor = '#ff0000';
        ctx.beginPath();
        ctx.arc(screenX + base.size * 0.5, screenY + base.size * 0.05, 4, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
        
        // Door
        ctx.fillStyle = '#4a3f35';
        ctx.fillRect(
          screenX + base.size * 0.42,
          screenY + base.size * 0.55,
          base.size * 0.16,
          base.size * 0.15
        );
        
        // Door handle
        ctx.fillStyle = '#ffd700';
        ctx.beginPath();
        ctx.arc(screenX + base.size * 0.46, screenY + base.size * 0.625, 2, 0, Math.PI * 2);
        ctx.fill();
        
        // Defensive turrets on corners
        for (let i = 0; i < 2; i++) {
          const turretX = screenX + base.size * (0.2 + i * 0.6);
          const turretY = screenY + base.size * 0.28;
          
          // Turret base
          ctx.fillStyle = '#2c3e50';
          ctx.fillRect(turretX - 6, turretY, 12, 8);
          
          // Turret barrel
          ctx.fillStyle = '#34495e';
          ctx.fillRect(turretX - 4, turretY - 5, 8, 5);
        }
        
        // Flag on top
        ctx.strokeStyle = '#8b4513';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(screenX + base.size * 0.75, screenY + base.size * 0.25);
        ctx.lineTo(screenX + base.size * 0.75, screenY + base.size * 0.12);
        ctx.stroke();
        
        // Flag fabric
        const flagWave = Math.sin(Date.now() / 150);
        ctx.fillStyle = '#ff0000';
        ctx.beginPath();
        ctx.moveTo(screenX + base.size * 0.75, screenY + base.size * 0.12);
        ctx.lineTo(screenX + base.size * 0.88 + flagWave * 2, screenY + base.size * 0.14);
        ctx.lineTo(screenX + base.size * 0.88 + flagWave * 2, screenY + base.size * 0.20);
        ctx.lineTo(screenX + base.size * 0.75, screenY + base.size * 0.22);
        ctx.closePath();
        ctx.fill();
        
        // Corner decorations
        const cornerSize = 8;
        ctx.fillStyle = '#ffd700';
        // Top-left
        ctx.fillRect(screenX, screenY, cornerSize, 2);
        ctx.fillRect(screenX, screenY, 2, cornerSize);
        // Top-right
        ctx.fillRect(screenX + base.size - cornerSize, screenY, cornerSize, 2);
        ctx.fillRect(screenX + base.size - 2, screenY, 2, cornerSize);
        // Bottom-left
        ctx.fillRect(screenX, screenY + base.size - 2, cornerSize, 2);
        ctx.fillRect(screenX, screenY + base.size - cornerSize, 2, cornerSize);
        // Bottom-right
        ctx.fillRect(screenX + base.size - cornerSize, screenY + base.size - 2, cornerSize, 2);
        ctx.fillRect(screenX + base.size - 2, screenY + base.size - cornerSize, 2, cornerSize);
        
        // Enhanced health bar
        const barWidth = base.size;
        const barHeight = 10;
        const barX = screenX;
        const barY = screenY - 18;
        
        // Health bar glow shadow
        ctx.shadowBlur = 8;
        ctx.shadowColor = 'rgba(0, 0, 0, 0.6)';
        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.fillRect(barX - 3, barY - 3, barWidth + 6, barHeight + 6);
        ctx.shadowBlur = 0;
        
        // Health bar background
        ctx.fillStyle = '#1a1a1a';
        ctx.fillRect(barX, barY, barWidth, barHeight);
        
        // Health bar fill with gradient
        const healthPercent = base.health / base.maxHealth;
        const healthGradient = ctx.createLinearGradient(barX, barY, barX + barWidth, barY);
        if (healthPercent > 0.7) {
          healthGradient.addColorStop(0, '#27ae60');
          healthGradient.addColorStop(0.5, '#2ecc71');
          healthGradient.addColorStop(1, '#1abc9c');
        } else if (healthPercent > 0.4) {
          healthGradient.addColorStop(0, '#f39c12');
          healthGradient.addColorStop(1, '#e67e22');
        } else {
          healthGradient.addColorStop(0, '#c0392b');
          healthGradient.addColorStop(1, '#e74c3c');
        }
        ctx.fillStyle = healthGradient;
        ctx.fillRect(barX, barY, barWidth * healthPercent, barHeight);
        
        // Health bar shine effect
        ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
        ctx.fillRect(barX, barY, barWidth * healthPercent, 3);
        
        // Health bar segmentation
        for (let i = 1; i < 10; i++) {
          ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)';
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(barX + (barWidth / 10) * i, barY);
          ctx.lineTo(barX + (barWidth / 10) * i, barY + barHeight);
          ctx.stroke();
        }
        
        // Health bar border
        ctx.strokeStyle = '#ecf0f1';
        ctx.lineWidth = 3;
        ctx.strokeRect(barX, barY, barWidth, barHeight);
        
        // Health text with shadow
        ctx.font = 'bold 12px Arial';
        ctx.textAlign = 'center';
        ctx.shadowBlur = 3;
        ctx.shadowColor = '#000';
        ctx.fillStyle = '#fff';
        ctx.fillText(`${Math.floor(base.health)}/${base.maxHealth}`, barX + barWidth/2, barY + barHeight/2 + 1);
        ctx.shadowBlur = 0;
        
        // Warning text if critical
        if (healthPercent < 0.3) {
          const warningAlpha = 0.5 + Math.sin(Date.now() / 150) * 0.5;
          ctx.globalAlpha = warningAlpha;
          ctx.font = 'bold 14px Arial';
          ctx.fillStyle = '#ff0000';
          ctx.strokeStyle = '#000';
          ctx.lineWidth = 3;
          ctx.strokeText('⚠️ CRITICAL!', screenX + base.size/2, screenY - 35);
          ctx.fillText('⚠️ CRITICAL!', screenX + base.size/2, screenY - 35);
          ctx.globalAlpha = 1;
        }
      });

      // Coins
      game.coinDrops.forEach(coin => {
        const screenX = coin.x - game.cameraX;
        const screenY = coin.y - game.cameraY;
        
        ctx.shadowBlur = 15;
        ctx.shadowColor = '#ffd700';
        ctx.fillStyle = '#ffd700';
        ctx.beginPath();
        ctx.arc(screenX, screenY, 8, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.fillStyle = '#ffed4e';
        ctx.beginPath();
        ctx.arc(screenX - 2, screenY - 2, 3, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.shadowBlur = 0;
        
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 10px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(coin.value, screenX, screenY + 20);
      });

      // Power-ups rendering
      game.powerUps.forEach(powerUp => {
        const screenX = powerUp.x - game.cameraX;
        const screenY = powerUp.y - game.cameraY;
        
        const pulse = Math.sin(Date.now() / 200) * 0.2 + 0.8;
        const float = Math.sin(Date.now() / 300 + powerUp.x) * 5;
        
        let icon, color;
        switch (powerUp.type) {
          case 'health':
            icon = '❤️';
            color = '#e74c3c';
            break;
          case 'speed':
            icon = '⚡';
            color = '#3498db';
            break;
          case 'damage':
            icon = '⚔️';
            color = '#f39c12';
            break;
          case 'firerate':
            icon = '🔥';
            color = '#9b59b6';
            break;
          case 'coins':
            icon = '💰';
            color = '#ffd700';
            break;
        }
        
        ctx.shadowBlur = 20 * pulse;
        ctx.shadowColor = color;
        
        // Glow circle
        ctx.fillStyle = color + '40';
        ctx.beginPath();
        ctx.arc(screenX, screenY + float, 20 * pulse, 0, Math.PI * 2);
        ctx.fill();
        
        // Icon
        ctx.font = 'bold 24px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(icon, screenX, screenY + float + 8);
        
        ctx.shadowBlur = 0;
        
        // Lifetime indicator
        if (powerUp.lifetime < 180) {
          ctx.fillStyle = `rgba(255, 255, 255, ${powerUp.lifetime / 180})`;
          ctx.font = '10px Arial';
          ctx.fillText(Math.ceil(powerUp.lifetime / 60) + 's', screenX, screenY + float + 25);
        }
      });

      // Particles
      game.particles.forEach(p => {
        const screenX = p.x - game.cameraX;
        const screenY = p.y - game.cameraY;
        
        if (p.isText) {
          // Text particles for XP gain
          ctx.globalAlpha = p.life / 60;
          ctx.font = 'bold 14px Arial';
          ctx.fillStyle = p.color;
          ctx.strokeStyle = '#000';
          ctx.lineWidth = 3;
          ctx.textAlign = 'center';
          ctx.strokeText(p.text, screenX, screenY);
          ctx.fillText(p.text, screenX, screenY);
        } else {
          // Regular particles
          ctx.fillStyle = p.color;
          ctx.globalAlpha = p.life / 40;
          ctx.beginPath();
          ctx.arc(screenX, screenY, p.size, 0, Math.PI * 2);
          ctx.fill();
        }
      });
      ctx.globalAlpha = 1;

      // Zombies with enhanced visuals
      game.zombies.forEach(zombie => {
        const screenX = zombie.x - game.cameraX;
        const screenY = zombie.y - game.cameraY;
        
        if (screenX > -50 && screenX < canvas.width + 50 && screenY > -50 && screenY < canvas.height + 50) {
          // Draw line to target with pulse effect
          if (zombie.targetLock && zombie.targetLock !== 'player' && zombie.attackCooldown > 20) {
            let targetScreenX, targetScreenY;
            let lineColor = '#ff0000';
            
            if (zombie.targetLock === 'base' && game.bases.length > 0) {
              const base = game.bases[0];
              targetScreenX = base.x + base.size/2 - game.cameraX;
              targetScreenY = base.y + base.size/2 - game.cameraY;
              lineColor = '#f39c12';
            } else if (zombie.targetLock === 'turret') {
              let closestTurret = null;
              let closestDist = Infinity;
              for (let turret of game.turrets) {
                const dist = Math.sqrt(
                  Math.pow(turret.x + turret.size/2 - zombie.x, 2) + 
                  Math.pow(turret.y + turret.size/2 - zombie.y, 2)
                );
                if (dist < closestDist) {
                  closestDist = dist;
                  closestTurret = turret;
                }
              }
              if (closestTurret) {
                targetScreenX = closestTurret.x + closestTurret.size/2 - game.cameraX;
                targetScreenY = closestTurret.y + closestTurret.size/2 - game.cameraY;
                lineColor = '#3498db';
              }
            } else if (zombie.targetLock === 'wall') {
              let closestWall = null;
              let closestDist = Infinity;
              for (let wall of game.walls) {
                const dist = Math.sqrt(
                  Math.pow(wall.x + wall.width/2 - zombie.x, 2) + 
                  Math.pow(wall.y + wall.height/2 - zombie.y, 2)
                );
                if (dist < closestDist) {
                  closestDist = dist;
                  closestWall = wall;
                }
              }
              if (closestWall) {
                targetScreenX = closestWall.x + closestWall.width/2 - game.cameraX;
                targetScreenY = closestWall.y + closestWall.height/2 - game.cameraY;
                lineColor = '#95a5a6';
              }
            }
            
            if (targetScreenX !== undefined && targetScreenY !== undefined) {
              const pulse = Math.sin(Date.now() / 200) * 0.3 + 0.7;
              ctx.strokeStyle = lineColor;
              ctx.lineWidth = 2;
              ctx.setLineDash([5, 5]);
              ctx.globalAlpha = 0.5 * pulse;
              ctx.beginPath();
              ctx.moveTo(screenX, screenY);
              ctx.lineTo(targetScreenX, targetScreenY);
              ctx.stroke();
              ctx.setLineDash([]);
              ctx.globalAlpha = 1;
            }
          }
          
          // Targeting player line with pulse
          if (zombie.targetLock === 'player') {
            const playerScreenX = game.player.x - game.cameraX;
            const playerScreenY = game.player.y - game.cameraY;
            const pulse = Math.sin(Date.now() / 150) * 0.4 + 0.6;
            ctx.strokeStyle = '#ff0000';
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 5]);
            ctx.globalAlpha = 0.5 * pulse;
            ctx.beginPath();
            ctx.moveTo(screenX, screenY);
            ctx.lineTo(playerScreenX, playerScreenY);
            ctx.stroke();
            ctx.setLineDash([]);
            ctx.globalAlpha = 1;
          }
          
          // Enhanced shadow with blur
          ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
          ctx.shadowBlur = 8;
          ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
          ctx.beginPath();
          ctx.ellipse(screenX, screenY + zombie.size + 5, zombie.size * 0.8, zombie.size * 0.3, 0, 0, Math.PI * 2);
          ctx.fill();
          ctx.shadowBlur = 0;
          
          // Zombie body with gradient
          const zombieGradient = ctx.createRadialGradient(screenX - zombie.size/3, screenY - zombie.size/3, 0, screenX, screenY, zombie.size);
          zombieGradient.addColorStop(0, lightenColor(zombie.color, 30));
          zombieGradient.addColorStop(0.7, zombie.color);
          zombieGradient.addColorStop(1, darkenColor(zombie.color, 30));
          ctx.fillStyle = zombieGradient;
          ctx.beginPath();
          ctx.arc(screenX, screenY, zombie.size, 0, Math.PI * 2);
          ctx.fill();
          
          // Boss/Megaboss enhanced outline with glow
          if (zombie.type === 'boss' || zombie.type === 'megaboss') {
            const glowIntensity = Math.sin(Date.now() / 300) * 0.2 + 0.8;
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = zombie.type === 'megaboss' ? 5 : 3;
            ctx.shadowBlur = (zombie.type === 'megaboss' ? 12 : 10) * glowIntensity;
            ctx.shadowColor = zombie.color;
            ctx.stroke();
            ctx.shadowBlur = 0;
          }
          
          // Glowing eyes with subtle animation
          const eyeGlow = Math.sin(Date.now() / 400) * 0.15 + 0.85;
          ctx.shadowBlur = 5 * eyeGlow;
          ctx.shadowColor = '#ff0000';
          ctx.fillStyle = '#ff0000';
          ctx.beginPath();
          ctx.arc(screenX - zombie.size/3, screenY - zombie.size/4, 4, 0, Math.PI * 2);
          ctx.arc(screenX + zombie.size/3, screenY - zombie.size/4, 4, 0, Math.PI * 2);
          ctx.fill();
          ctx.shadowBlur = 0;
          
          // Status effect indicators
          if (zombie.poisoned) {
            ctx.strokeStyle = '#00ff00';
            ctx.lineWidth = 3;
            ctx.shadowBlur = 10;
            ctx.shadowColor = '#00ff00';
            ctx.beginPath();
            ctx.arc(screenX, screenY, zombie.size + 5, 0, Math.PI * 2);
            ctx.stroke();
            ctx.shadowBlur = 0;
            
            ctx.font = 'bold 14px Arial';
            ctx.fillStyle = '#00ff00';
            ctx.fillText('☠️', screenX + zombie.size, screenY - zombie.size);
          }
          
          if (zombie.frozen) {
            ctx.strokeStyle = '#00ffff';
            ctx.lineWidth = 3;
            ctx.shadowBlur = 15;
            ctx.shadowColor = '#00ffff';
            ctx.beginPath();
            ctx.arc(screenX, screenY, zombie.size + 5, 0, Math.PI * 2);
            ctx.stroke();
            ctx.shadowBlur = 0;
            
            ctx.font = 'bold 14px Arial';
            ctx.fillStyle = '#00ffff';
            ctx.fillText('❄️', screenX - zombie.size, screenY - zombie.size);
          }
          
          // Target indicator
          if (zombie.targetLock && typeof zombie.targetLock === 'string') {
            let iconText = '';
            let iconColor = '';
            if (zombie.targetLock === 'base') {
              iconText = '🏠';
              iconColor = '#f39c12';
            } else if (zombie.targetLock === 'turret') {
              iconText = '🔫';
              iconColor = '#3498db';
            } else if (zombie.targetLock === 'wall') {
              iconText = '🧱';
              iconColor = '#95a5a6';
            } else if (zombie.targetLock === 'player') {
              iconText = '👤';
              iconColor = '#e74c3c';
            }
            
            if (iconText) {
              ctx.font = 'bold 16px Arial';
              ctx.textAlign = 'center';
              ctx.fillStyle = iconColor;
              ctx.strokeStyle = '#000';
              ctx.lineWidth = 2;
              ctx.strokeText(iconText, screenX, screenY + zombie.size + 25);
              ctx.fillText(iconText, screenX, screenY + zombie.size + 25);
            }
          }
          
          // Special zombie type indicators
          if (zombie.type === 'healer') {
            // Healing pulse effect - enhanced
            const healPulse = Math.sin(Date.now() / 300) * 0.3 + 0.7;
            ctx.strokeStyle = `rgba(46, 204, 113, ${0.4 * healPulse})`;
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(screenX, screenY, zombie.healRange * healPulse * 0.3, 0, Math.PI * 2);
            ctx.stroke();
            
            // Stronger visual when actively healing
            if (zombie.healCooldown > 0) {
              const activeGlow = Math.sin(Date.now() / 100) * 0.5 + 0.5;
              ctx.shadowBlur = 20 * activeGlow;
              ctx.shadowColor = '#2ecc71';
              ctx.strokeStyle = `rgba(46, 204, 113, ${0.8 * activeGlow})`;
              ctx.lineWidth = 4;
              ctx.beginPath();
              ctx.arc(screenX, screenY, zombie.size + 8, 0, Math.PI * 2);
              ctx.stroke();
              ctx.shadowBlur = 0;
            }
            
            ctx.font = 'bold 16px Arial';
            ctx.fillStyle = '#2ecc71';
            ctx.strokeStyle = '#000';
            ctx.lineWidth = 3;
            ctx.strokeText('✚', screenX, screenY - zombie.size - 5);
            ctx.fillText('✚', screenX, screenY - zombie.size - 5);
            ctx.shadowBlur = 0;
          } else if (zombie.type === 'armored') {
            // Armor plating
            ctx.strokeStyle = '#7f8c8d';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(screenX, screenY, zombie.size + 2, 0, Math.PI * 2);
            ctx.stroke();
          } else if (zombie.type === 'berserker') {
            // Rage aura
            const healthPercent = zombie.health / zombie.maxHealth;
            if (healthPercent < 0.5) {
              const rageIntensity = (1 - healthPercent) * 2;
              ctx.shadowBlur = 15 * rageIntensity;
              ctx.shadowColor = '#e74c3c';
              ctx.strokeStyle = `rgba(231, 76, 60, ${0.5 * rageIntensity})`;
              ctx.lineWidth = 3;
              ctx.beginPath();
              ctx.arc(screenX, screenY, zombie.size + 5, 0, Math.PI * 2);
              ctx.stroke();
              ctx.shadowBlur = 0;
            }
          } else if (zombie.type === 'necromancer') {
            // Purple aura
            const necroGlow = Math.sin(Date.now() / 400) * 0.3 + 0.7;
            ctx.shadowBlur = 20 * necroGlow;
            ctx.shadowColor = '#9b59b6';
            ctx.strokeStyle = `rgba(155, 89, 182, ${0.4 * necroGlow})`;
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(screenX, screenY, zombie.size + 8, 0, Math.PI * 2);
            ctx.stroke();
            ctx.shadowBlur = 0;
            
            ctx.font = 'bold 16px Arial';
            ctx.fillStyle = '#9b59b6';
            ctx.fillText('☠️', screenX, screenY - zombie.size - 5);
          } else if (zombie.type === 'shielded' && zombie.hasShield) {
            // Shield indicator
            ctx.fillStyle = 'rgba(22, 160, 133, 0.3)';
            ctx.beginPath();
            ctx.arc(screenX, screenY, zombie.size + 6, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.font = 'bold 16px Arial';
            ctx.fillStyle = '#16a085';
            ctx.fillText('🛡️', screenX, screenY - zombie.size - 5);
          } else if (zombie.type === 'splitter') {
            ctx.font = 'bold 14px Arial';
            ctx.fillStyle = '#e67e22';
            ctx.fillText('⚡', screenX, screenY - zombie.size - 5);
          }
          
          const barWidth = zombie.size * 2;
          const barHeight = 6;
          const barX = screenX - zombie.size;
          const barY = screenY - zombie.size - 15;
          
          ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
          ctx.fillRect(barX - 1, barY - 1, barWidth + 2, barHeight + 2);
          
          ctx.fillStyle = '#e74c3c';
          ctx.fillRect(barX, barY, barWidth, barHeight);
          
          const healthPercent = zombie.health / zombie.maxHealth;
          ctx.fillStyle = '#2ecc71';
          ctx.fillRect(barX, barY, barWidth * healthPercent, barHeight);
          
          ctx.strokeStyle = '#fff';
          ctx.lineWidth = 1;
          ctx.strokeRect(barX, barY, barWidth, barHeight);
        }
      });

      // Bullets with enhanced visuals and trails
      game.bullets.forEach(bullet => {
        const screenX = bullet.x - game.cameraX;
        const screenY = bullet.y - game.cameraY;
        
        let bulletColor, bulletSize, shadowBlur, trailLength;
        if (bullet.fromTurret) {
          bulletColor = bullet.explosive ? '#ff3300' : '#00ff88';
          bulletSize = 7;
          shadowBlur = 12;
          trailLength = 2;
        } else {
          // Special bullet colors
          if (bullet.homing) bulletColor = '#ff00ff';
          else if (bullet.poison) bulletColor = '#00ff00';
          else if (bullet.freeze) bulletColor = '#00ffff';
          else if (bullet.split) bulletColor = '#ffaa00';
          else if (bullet.cluster) bulletColor = '#ff6600';
          else bulletColor = bullet.isCrit ? '#ffff00' : bullet.explosive ? '#ff6600' : '#ffd700';
          
          bulletSize = bullet.isCrit ? 6 : 4;
          shadowBlur = bullet.isCrit ? 10 : 6;
          trailLength = bullet.homing ? 4 : bullet.isCrit ? 3 : 2;
        }
        
        // Enhanced bullet trail effect
        ctx.globalAlpha = 0.6;
        for (let i = 0; i < trailLength; i++) {
          const trailX = screenX - bullet.vx * i * 2;
          const trailY = screenY - bullet.vy * i * 2;
          const trailSize = bulletSize * (1 - i / trailLength);
          const trailAlpha = 0.6 * (1 - i / trailLength);
          
          ctx.globalAlpha = trailAlpha;
          
          // Trail glow
          const trailGrad = ctx.createRadialGradient(trailX, trailY, 0, trailX, trailY, trailSize * 2);
          trailGrad.addColorStop(0, bulletColor);
          trailGrad.addColorStop(1, bulletColor + '00');
          ctx.fillStyle = trailGrad;
          ctx.beginPath();
          ctx.arc(trailX, trailY, trailSize * 2, 0, Math.PI * 2);
          ctx.fill();
          
          // Trail core
          ctx.fillStyle = bulletColor;
          ctx.shadowBlur = shadowBlur * 0.5 * (1 - i / trailLength);
          ctx.shadowColor = bulletColor;
          ctx.beginPath();
          ctx.arc(trailX, trailY, trailSize, 0, Math.PI * 2);
          ctx.fill();
        }
        ctx.globalAlpha = 1;
        
        // Main bullet with enhanced glow
        const bulletGrad = ctx.createRadialGradient(screenX, screenY, 0, screenX, screenY, bulletSize * 2);
        bulletGrad.addColorStop(0, '#ffffff');
        bulletGrad.addColorStop(0.3, bulletColor);
        bulletGrad.addColorStop(1, bulletColor + '00');
        ctx.fillStyle = bulletGrad;
        ctx.beginPath();
        ctx.arc(screenX, screenY, bulletSize * 2, 0, Math.PI * 2);
        ctx.fill();
        
        // Bullet core
        ctx.shadowBlur = shadowBlur;
        ctx.shadowColor = bulletColor;
        ctx.fillStyle = bulletColor;
        ctx.beginPath();
        ctx.arc(screenX, screenY, bulletSize, 0, Math.PI * 2);
        ctx.fill();
        
        // Inner bright core
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(screenX - bulletSize * 0.3, screenY - bulletSize * 0.3, bulletSize * 0.4, 0, Math.PI * 2);
        ctx.fill();
        
        // Special effects for different bullet types
        if (bullet.homing) {
          // Homing indicator
          ctx.strokeStyle = 'rgba(255, 0, 255, 0.5)';
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.arc(screenX, screenY, bulletSize + 4, 0, Math.PI * 2);
          ctx.stroke();
        } else if (bullet.poison) {
          // Poison drip
          ctx.fillStyle = '#00ff00';
          for (let i = 0; i < 3; i++) {
            const angle = (Date.now() / 100 + i) * Math.PI * 2 / 3;
            ctx.fillRect(
              screenX + Math.cos(angle) * bulletSize,
              screenY + Math.sin(angle) * bulletSize,
              1, 3
            );
          }
        } else if (bullet.freeze) {
          // Ice crystals
          ctx.strokeStyle = '#00ffff';
          ctx.lineWidth = 1;
          for (let i = 0; i < 4; i++) {
            const angle = (i / 4) * Math.PI * 2;
            ctx.beginPath();
            ctx.moveTo(screenX, screenY);
            ctx.lineTo(
              screenX + Math.cos(angle) * (bulletSize + 3),
              screenY + Math.sin(angle) * (bulletSize + 3)
            );
            ctx.stroke();
          }
        }
        
        // Outer glow ring for turret bullets
        if (bullet.fromTurret) {
          ctx.globalAlpha = 0.3;
          ctx.beginPath();
          ctx.arc(screenX, screenY, bulletSize + 6, 0, Math.PI * 2);
          ctx.fill();
          ctx.globalAlpha = 1;
        }
        
        // Critical hit enhanced sparkle effect
        if (bullet.isCrit) {
          const sparkleTime = Date.now() / 100;
          for (let i = 0; i < 8; i++) {
            const angle = (i / 8) * Math.PI * 2 + sparkleTime;
            const sparkleX = screenX + Math.cos(angle) * 8;
            const sparkleY = screenY + Math.sin(angle) * 8;
            ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
            ctx.fillRect(sparkleX - 1.5, sparkleY - 1.5, 3, 3);
          }
          
          // Rotating star
          ctx.save();
          ctx.translate(screenX, screenY);
          ctx.rotate(sparkleTime);
          ctx.fillStyle = 'rgba(255, 255, 0, 0.6)';
          for (let i = 0; i < 4; i++) {
            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(Math.cos(i * Math.PI / 2) * 10, Math.sin(i * Math.PI / 2) * 10);
            ctx.lineTo(Math.cos((i + 1) * Math.PI / 2) * 10, Math.sin((i + 1) * Math.PI / 2) * 10);
            ctx.fill();
          }
          ctx.restore();
        }
        
        ctx.shadowBlur = 0;
      });

      // BUILD PREVIEW
      const preview = game.buildPreview;
      if (preview.active && gameState === 'playing') {
        const item = buildItems.find(b => b.id === preview.type);
        if (item) {
          let worldX = game.mouseX + game.cameraX;
          let worldY = game.mouseY + game.cameraY;
          
          const gridSize = 50;
          worldX = Math.floor(worldX / gridSize) * gridSize;
          worldY = Math.floor(worldY / gridSize) * gridSize;
          
          const previewX = worldX - game.cameraX;
          const previewY = worldY - game.cameraY;
          
          let canPlace = coins >= item.cost;
          let validationMessage = 'OK';
          
          if (item.type === 'base') {
            if (!game.bases) game.bases = [];
            if (game.bases.length > 0) {
              canPlace = false;
              validationMessage = 'Base already placed';
            } else {
              const overlapCheck = checkStructureOverlap(worldX, worldY, 100, 100, 'base');
              canPlace = canPlace && overlapCheck.valid;
              validationMessage = overlapCheck.reason;
            }
          } else if (item.type === 'turret') {
            const overlapCheck = checkStructureOverlap(worldX, worldY, 50, 50, 'turret');
            canPlace = canPlace && overlapCheck.valid;
            validationMessage = overlapCheck.reason;
          } else if (item.type === 'wall') {
            const currentRotation = preview.rotation || 0;
            const isHorizontal = currentRotation % 180 === 0;
            const w = isHorizontal ? 100 : 50;
            const h = isHorizontal ? 50 : 100;
            const overlapCheck = checkStructureOverlap(worldX, worldY, w, h, 'wall');
            canPlace = canPlace && overlapCheck.valid;
            validationMessage = overlapCheck.reason;
          }
          
          ctx.save();
          ctx.globalAlpha = 0.8;
          
          if (item.type === 'turret') {
            ctx.strokeStyle = canPlace ? 'rgba(78, 204, 163, 0.6)' : 'rgba(231, 76, 60, 0.6)';
            ctx.lineWidth = 3;
            ctx.strokeRect(previewX, previewY, 50, 50);
            
            // Always show range during turret placement preview
            ctx.strokeStyle = canPlace ? 'rgba(78, 204, 163, 0.4)' : 'rgba(231, 76, 60, 0.4)';
            ctx.lineWidth = 2;
            ctx.setLineDash([10, 5]);
            ctx.beginPath();
            ctx.arc(previewX + 25, previewY + 25, item.stats.range, 0, Math.PI * 2);
            ctx.stroke();
            ctx.setLineDash([]);
            
            ctx.fillStyle = canPlace ? '#4ecca3' : '#e74c3c';
            ctx.shadowBlur = 20;
            ctx.shadowColor = canPlace ? '#4ecca3' : '#e74c3c';
            ctx.fillRect(previewX, previewY, 50, 50);
            
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 3;
            ctx.strokeRect(previewX, previewY, 50, 50);
            
            ctx.shadowBlur = 0;
            ctx.save();
            ctx.translate(previewX + 25, previewY + 25);
            ctx.rotate((preview.rotation || 0) * Math.PI / 180);
            ctx.fillStyle = '#34495e';
            ctx.fillRect(0, -4, 20, 8);
            ctx.fillStyle = canPlace ? '#4ecca3' : '#e74c3c';
            ctx.fillRect(15, -3, 5, 6);
            ctx.restore();
            
            ctx.font = 'bold 32px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = '#fff';
            ctx.fillText(item.icon, previewX + 25, previewY + 25);
            
            ctx.font = 'bold 14px Arial';
            ctx.fillStyle = '#fff';
            ctx.strokeStyle = '#000';
            ctx.lineWidth = 3;
            const rangeText = `Range: ${item.stats.range}px`;
            ctx.strokeText(rangeText, previewX + 25, previewY + 70);
            ctx.fillText(rangeText, previewX + 25, previewY + 70);
            
          } else if (item.type === 'wall') {
            const currentRotation = preview.rotation || 0;
            const isHorizontal = currentRotation % 180 === 0;
            const w = isHorizontal ? 100 : 50;
            const h = isHorizontal ? 50 : 100;
            
            ctx.fillStyle = canPlace ? item.color + 'CC' : '#e74c3cCC';
            ctx.shadowBlur = 20;
            ctx.shadowColor = canPlace ? item.color : '#e74c3c';
            ctx.fillRect(previewX, previewY, w, h);
            
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 3;
            ctx.strokeRect(previewX, previewY, w, h);
            
            ctx.shadowBlur = 0;
            ctx.font = 'bold 30px Arial';
            ctx.textAlign = 'center';
            ctx.fillStyle = '#ffffff';
            ctx.fillText(item.icon, previewX + w/2, previewY + h/2 + 10);
            
            ctx.save();
            ctx.translate(previewX + w/2, previewY + h/2);
            ctx.rotate(currentRotation * Math.PI / 180);
            
            const flashIntensity = game.rotationFlash / 30;
            const baseAlpha = 0.8 + (flashIntensity * 0.2);
            ctx.globalAlpha = baseAlpha;
            
            ctx.strokeStyle = flashIntensity > 0 ? '#ffff00' : '#00ffff';
            ctx.lineWidth = 3 + (flashIntensity * 2);
            ctx.beginPath();
            ctx.moveTo(0, -20);
            ctx.lineTo(0, 20);
            ctx.stroke();
            
            ctx.beginPath();
            ctx.moveTo(0, -20);
            ctx.lineTo(-5, -15);
            ctx.moveTo(0, -20);
            ctx.lineTo(5, -15);
            ctx.stroke();
            
            ctx.restore();
            
            ctx.font = 'bold 12px Arial';
            ctx.fillStyle = '#ffff00';
            ctx.strokeStyle = '#000';
            ctx.lineWidth = 3;
            const tierText = `Starts as Wood Wall | Click to Upgrade Later`;
            ctx.strokeText(tierText, previewX + w/2, previewY - 25);
            ctx.fillText(tierText, previewX + w/2, previewY - 25);
            
            const rotText = `${currentRotation}° (Press R)`;
            ctx.strokeText(rotText, previewX + w/2, previewY - 10);
            ctx.fillText(rotText, previewX + w/2, previewY - 10);
            
          } else if (item.type === 'trap') {
            ctx.fillStyle = canPlace ? 'rgba(192, 57, 43, 0.5)' : 'rgba(231, 76, 60, 0.5)';
            ctx.shadowBlur = 20;
            ctx.shadowColor = canPlace ? '#c0392b' : '#e74c3c';
            ctx.beginPath();
            ctx.arc(previewX + 25, previewY + 25, 25, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.strokeStyle = canPlace ? '#c0392b' : '#e74c3c';
            ctx.lineWidth = 3;
            ctx.stroke();
            
            ctx.shadowBlur = 0;
            ctx.font = 'bold 24px Arial';
            ctx.textAlign = 'center';
            ctx.fillStyle = '#fff';
            ctx.fillText(item.icon, previewX + 25, previewY + 32);
            
          } else if (item.type === 'base') {
            const baseSize = 100;
            const alreadyHasBase = game.bases && game.bases.length > 0;
            const actuallyCanPlace = canPlace && !alreadyHasBase;
            
            // Always show safe zone preview circle during base placement
            ctx.strokeStyle = actuallyCanPlace ? 'rgba(0, 255, 150, 0.3)' : 'rgba(255, 100, 100, 0.3)';
            ctx.lineWidth = 3;
            ctx.setLineDash([10, 10]);
            ctx.beginPath();
            ctx.arc(previewX + baseSize/2, previewY + baseSize/2, 400, 0, Math.PI * 2);
            ctx.stroke();
            ctx.setLineDash([]);
            
            // Safe zone fill
            ctx.fillStyle = actuallyCanPlace ? 'rgba(0, 255, 150, 0.05)' : 'rgba(255, 100, 100, 0.05)';
            ctx.beginPath();
            ctx.arc(previewX + baseSize/2, previewY + baseSize/2, 400, 0, Math.PI * 2);
            ctx.fill();
            
            // Safe zone label
            ctx.font = 'bold 12px Arial';
            ctx.textAlign = 'center';
            ctx.fillStyle = actuallyCanPlace ? '#00ff96' : '#ff6464';
            ctx.strokeStyle = '#000';
            ctx.lineWidth = 3;
            ctx.strokeText('🛡️ Safe Zone', previewX + baseSize/2, previewY + baseSize/2 - 220);
            ctx.fillText('🛡️ Safe Zone', previewX + baseSize/2, previewY + baseSize/2 - 220);
            
            ctx.fillStyle = actuallyCanPlace ? '#f39c12' : '#e74c3c';
            ctx.shadowBlur = 25;
            ctx.shadowColor = actuallyCanPlace ? '#f39c12' : '#e74c3c';
            ctx.fillRect(previewX, previewY, baseSize, baseSize);
            
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 4;
            ctx.strokeRect(previewX, previewY, baseSize, baseSize);
            
            ctx.shadowBlur = 0;
            ctx.font = 'bold 48px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = '#fff';
            ctx.fillText(item.icon, previewX + baseSize/2, previewY + baseSize/2);
            
            ctx.font = 'bold 16px Arial';
            ctx.fillStyle = '#fff';
            ctx.strokeStyle = '#000';
            ctx.lineWidth = 3;
            ctx.strokeText('2×2', previewX + baseSize/2, previewY + baseSize + 20);
            ctx.fillText('2×2', previewX + baseSize/2, previewY + baseSize + 20);
            
            if (alreadyHasBase) {
              ctx.font = 'bold 14px Arial';
              ctx.fillStyle = '#ff0000';
              ctx.strokeStyle = '#000';
              ctx.lineWidth = 3;
              ctx.strokeText('BASE ALREADY PLACED', previewX + baseSize/2, previewY - 20);
              ctx.fillText('BASE ALREADY PLACED', previewX + baseSize/2, previewY - 20);
            }
          }
          
          ctx.shadowBlur = 0;
          ctx.font = 'bold 16px Arial';
          ctx.textAlign = 'center';
          ctx.fillStyle = canPlace ? '#00ff00' : '#ff0000';
          ctx.strokeStyle = '#000';
          ctx.lineWidth = 4;
          const statusText = canPlace ? '✓ CLICK TO PLACE' : `✗ ${validationMessage.toUpperCase()}`;
          ctx.strokeText(statusText, previewX, previewY - 60);
          ctx.fillText(statusText, previewX, previewY - 60);
          
          ctx.font = 'bold 14px Arial';
          ctx.fillStyle = coins >= item.cost ? '#ffff00' : '#ff0000';
          const costText = `Cost: ${item.cost} 💰`;
          ctx.strokeText(costText, previewX, previewY - 40);
          ctx.fillText(costText, previewX, previewY - 40);
          
          ctx.restore();
        }
      }

      // Player with enhanced visuals
      const screenPlayerX = game.player.x - game.cameraX;
      const screenPlayerY = game.player.y - game.cameraY;
      const angle = Math.atan2(game.mouseY - screenPlayerY, game.mouseX - screenPlayerX);
      
      // Laser sight
      if (game.player.laserSight) {
        ctx.strokeStyle = 'rgba(255, 0, 0, 0.3)';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.moveTo(screenPlayerX, screenPlayerY);
        ctx.lineTo(screenPlayerX + Math.cos(angle) * 500, screenPlayerY + Math.sin(angle) * 500);
        ctx.stroke();
        ctx.setLineDash([]);
        
        // Laser dot
        const dotX = screenPlayerX + Math.cos(angle) * 500;
        const dotY = screenPlayerY + Math.sin(angle) * 500;
        ctx.fillStyle = 'rgba(255, 0, 0, 0.8)';
        ctx.beginPath();
        ctx.arc(dotX, dotY, 3, 0, Math.PI * 2);
        ctx.fill();
      }
      
      // Orbital bullets
      if (game.player.orbital && game.player.orbitalBullets.length > 0) {
        game.player.orbitalBullets.forEach(orbital => {
          const orbitalX = screenPlayerX + Math.cos(orbital.angle) * orbital.distance;
          const orbitalY = screenPlayerY + Math.sin(orbital.angle) * orbital.distance;
          
          ctx.shadowBlur = 15;
          ctx.shadowColor = '#00ffff';
          ctx.fillStyle = '#00ffff';
          ctx.beginPath();
          ctx.arc(orbitalX, orbitalY, 6, 0, Math.PI * 2);
          ctx.fill();
          ctx.shadowBlur = 0;
          
          // Trail
          ctx.strokeStyle = 'rgba(0, 255, 255, 0.3)';
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.arc(screenPlayerX, screenPlayerY, orbital.distance, 0, Math.PI * 2);
          ctx.stroke();
        });
      }
      
      let playerInsideWall = false;
      for (let wall of game.walls) {
        if (game.player.x + game.player.size > wall.x && game.player.x - game.player.size < wall.x + wall.width &&
            game.player.y + game.player.size > wall.y && game.player.y - game.player.size < wall.y + wall.height) {
          playerInsideWall = true;
          break;
        }
      }
      
      // Hopper range indicator with animated ring
      if (game.player.hopperRange > 0) {
        const pulseScale = 1 + Math.sin(Date.now() / 500) * 0.03;
        ctx.strokeStyle = 'rgba(0, 255, 100, 0.3)';
        ctx.lineWidth = 2;
        ctx.setLineDash([10, 10]);
        ctx.beginPath();
        ctx.arc(screenPlayerX, screenPlayerY, game.player.hopperRange * pulseScale, 0, Math.PI * 2);
        ctx.stroke();
        ctx.setLineDash([]);
        
        // Subtle magnetic field effect
        for (let i = 0; i < 4; i++) {
          const rippleAngle = (i / 4) * Math.PI * 2 + Date.now() / 1500;
          const rippleX = screenPlayerX + Math.cos(rippleAngle) * game.player.hopperRange * 0.7;
          const rippleY = screenPlayerY + Math.sin(rippleAngle) * game.player.hopperRange * 0.7;
          ctx.fillStyle = 'rgba(0, 255, 100, 0.2)';
          ctx.beginPath();
          ctx.arc(rippleX, rippleY, 2, 0, Math.PI * 2);
          ctx.fill();
        }
        
        ctx.fillStyle = 'rgba(0, 255, 100, 0.8)';
        ctx.font = 'bold 20px Arial';
        ctx.textAlign = 'center';
        ctx.shadowBlur = 5;
        ctx.shadowColor = '#00ff64';
        ctx.fillText('🧲', screenPlayerX, screenPlayerY - game.player.size - 30);
        ctx.shadowBlur = 0;
        
        ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
        ctx.font = 'bold 12px Arial';
        ctx.fillText(`Lv${game.player.hopperLevel}`, screenPlayerX, screenPlayerY - game.player.size - 15);
      }
      
      // Enhanced shadow with blur
      ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
      ctx.shadowBlur = 12;
      ctx.shadowColor = 'rgba(0, 0, 0, 0.6)';
      ctx.beginPath();
      ctx.ellipse(screenPlayerX, screenPlayerY + game.player.size + 5, game.player.size * 0.8, game.player.size * 0.3, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;
      
      ctx.save();
      ctx.translate(screenPlayerX, screenPlayerY);
      ctx.rotate(angle);
      
      if (playerInsideWall) {
        ctx.shadowBlur = 15;
        ctx.shadowColor = '#00ffff';
        ctx.globalAlpha = 0.8;
      }
      
      const rageGlow = game.player.rage / game.player.maxRage;
      if (rageGlow > 0 && !playerInsideWall) {
        ctx.shadowBlur = 20 * rageGlow;
        ctx.shadowColor = '#ff0000';
      }
      
      // Berserker glow with subtle pulse
      if (game.player.berserker && game.player.health < game.player.maxHealth * 0.3) {
        const berserkPulse = Math.sin(Date.now() / 200) * 0.2 + 0.8;
        ctx.shadowBlur = 20 * berserkPulse;
        ctx.shadowColor = '#ff0000';
      }
      
      // Main body - armored suit with detail
      const bodyGradient = ctx.createRadialGradient(
        -game.player.size/2, -game.player.size/4, 0,
        0, 0, game.player.size * 1.5
      );
      bodyGradient.addColorStop(0, '#ff8080');
      bodyGradient.addColorStop(0.4, '#ff6b6b');
      bodyGradient.addColorStop(0.7, '#e74c3c');
      bodyGradient.addColorStop(1, '#c0392b');
      ctx.fillStyle = bodyGradient;
      
      // Torso - rounded rectangle with shoulder pads
      ctx.beginPath();
      ctx.roundRect(-game.player.size * 1.1, -game.player.size * 0.6, game.player.size * 2.2, game.player.size * 1.2, 8);
      ctx.fill();
      
      // Shoulder pads
      ctx.fillStyle = '#8B0000';
      ctx.beginPath();
      ctx.ellipse(-game.player.size * 0.9, -game.player.size * 0.5, game.player.size * 0.3, game.player.size * 0.4, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.ellipse(-game.player.size * 0.9, game.player.size * 0.5, game.player.size * 0.3, game.player.size * 0.4, 0, 0, Math.PI * 2);
      ctx.fill();
      
      // Chest armor plate
      const chestGrad = ctx.createLinearGradient(-game.player.size * 0.5, -game.player.size * 0.3, game.player.size * 0.3, game.player.size * 0.3);
      chestGrad.addColorStop(0, '#b22222');
      chestGrad.addColorStop(0.5, '#a52a2a');
      chestGrad.addColorStop(1, '#8b1a1a');
      ctx.fillStyle = chestGrad;
      ctx.fillRect(-game.player.size * 0.5, -game.player.size * 0.3, game.player.size * 0.8, game.player.size * 0.6);
      
      // Armor detail lines
      ctx.strokeStyle = '#FFD700';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(-game.player.size * 0.5, 0);
      ctx.lineTo(game.player.size * 0.3, 0);
      ctx.stroke();
      
      // Visor/helmet glow
      ctx.fillStyle = '#00ffff';
      ctx.shadowBlur = 10;
      ctx.shadowColor = '#00ffff';
      ctx.fillRect(-game.player.size * 0.4, -game.player.size * 0.15, game.player.size * 0.6, game.player.size * 0.1);
      ctx.shadowBlur = 0;
      
      // Backpack/jetpack
      ctx.fillStyle = '#2c3e50';
      ctx.fillRect(-game.player.size * 1.1, -game.player.size * 0.4, game.player.size * 0.3, game.player.size * 0.8);
      
      // Exhaust ports
      for (let i = 0; i < 2; i++) {
        ctx.fillStyle = '#ff6600';
        ctx.beginPath();
        ctx.arc(-game.player.size * 1.05, -game.player.size * 0.2 + i * game.player.size * 0.4, 4, 0, Math.PI * 2);
        ctx.fill();
      }
      
      // Enhanced gun with detailed parts
      const gunGradient = ctx.createLinearGradient(game.player.size/2, -game.player.size/3, game.player.size * 1.5, game.player.size/3);
      gunGradient.addColorStop(0, '#95a5a6');
      gunGradient.addColorStop(0.3, '#7f8c8d');
      gunGradient.addColorStop(0.6, '#5a6c7d');
      gunGradient.addColorStop(1, '#34495e');
      ctx.fillStyle = gunGradient;
      ctx.shadowBlur = 5;
      ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
      
      // Gun body
      ctx.beginPath();
      ctx.roundRect(game.player.size * 0.4, -game.player.size * 0.35, game.player.size * 1.1, game.player.size * 0.7, 5);
      ctx.fill();
      ctx.shadowBlur = 0;
      
      // Magazine
      ctx.fillStyle = '#2c3e50';
      ctx.fillRect(game.player.size * 0.5, game.player.size * 0.1, game.player.size * 0.3, game.player.size * 0.4);
      
      // Scope/sight
      ctx.fillStyle = '#1a252f';
      ctx.beginPath();
      ctx.roundRect(game.player.size * 0.8, -game.player.size * 0.45, game.player.size * 0.4, game.player.size * 0.25, 3);
      ctx.fill();
      
      // Red dot
      ctx.fillStyle = '#ff0000';
      ctx.beginPath();
      ctx.arc(game.player.size, -game.player.size * 0.33, 3, 0, Math.PI * 2);
      ctx.fill();
      
      // Gun barrel with detail
      ctx.fillStyle = '#1a252f';
      ctx.shadowBlur = 3;
      ctx.shadowColor = 'rgba(0, 0, 0, 0.7)';
      ctx.fillRect(game.player.size * 1.4, -game.player.size * 0.2, game.player.size * 0.45, game.player.size * 0.4);
      ctx.shadowBlur = 0;
      
      // Barrel tip with suppressor
      ctx.fillStyle = '#34495e';
      ctx.fillRect(game.player.size * 1.75, -game.player.size * 0.15, game.player.size * 0.15, game.player.size * 0.3);
      
      // Muzzle brake
      ctx.fillStyle = '#95a5a6';
      ctx.fillRect(game.player.size * 1.85, -game.player.size * 0.12, game.player.size * 0.08, game.player.size * 0.24);
      
      // Tactical rail
      ctx.fillStyle = '#2c3e50';
      ctx.fillRect(game.player.size * 0.6, -game.player.size * 0.38, game.player.size * 0.7, game.player.size * 0.08);
      
      // Stock/grip details
      ctx.fillStyle = '#8B4513';
      ctx.fillRect(game.player.size * 0.35, -game.player.size * 0.25, game.player.size * 0.15, game.player.size * 0.5);
      
      // Metallic shine on gun
      ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
      ctx.fillRect(game.player.size * 0.5, -game.player.size * 0.33, game.player.size * 0.8, 3);
      
      // Muzzle flash when shooting
      if (Date.now() - game.lastShot < 100) {
        ctx.shadowBlur = 20;
        ctx.shadowColor = '#ffff00';
        ctx.fillStyle = '#ffff00';
        ctx.beginPath();
        ctx.arc(game.player.size * 1.9, 0, 8, 0, Math.PI * 2);
        ctx.fill();
        
        // Flash particles
        for (let i = 0; i < 4; i++) {
          const flashAngle = (i / 4) * Math.PI * 2;
          ctx.fillStyle = '#ff9900';
          ctx.beginPath();
          ctx.arc(
            game.player.size * 1.9 + Math.cos(flashAngle) * 12,
            Math.sin(flashAngle) * 12,
            3, 0, Math.PI * 2
          );
          ctx.fill();
        }
        ctx.shadowBlur = 0;
      }
      
      // Ammo belt
      ctx.strokeStyle = '#DAA520';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(0, 0, game.player.size * 0.7, -Math.PI * 0.3, Math.PI * 0.3);
      ctx.stroke();
      
      ctx.restore();
      
      if (playerInsideWall) {
        ctx.font = 'bold 12px Arial';
        ctx.fillStyle = '#00ffff';
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 3;
        ctx.textAlign = 'center';
        ctx.strokeText('👻 GHOST MODE', screenPlayerX, screenPlayerY - game.player.size - 40);
        ctx.fillText('👻 GHOST MODE', screenPlayerX, screenPlayerY - game.player.size - 40);
      }
      
      // MULTIPLAYER: Render other players
      // Object.entries(game.otherPlayers).forEach(([otherPlayerId, otherPlayer]) => {
      //   const otherScreenX = otherPlayer.x - game.cameraX;
      //   const otherScreenY = otherPlayer.y - game.cameraY;
      //   
      //   // Draw other player with different color
      //   ctx.fillStyle = '#00ff00'; // Green for teammates
      //   ctx.beginPath();
      //   ctx.arc(otherScreenX, otherScreenY, 20, 0, Math.PI * 2);
      //   ctx.fill();
      //   
      //   // Player name
      //   ctx.font = 'bold 12px Arial';
      //   ctx.fillStyle = '#fff';
      //   ctx.strokeStyle = '#000';
      //   ctx.lineWidth = 3;
      //   ctx.textAlign = 'center';
      //   ctx.strokeText(otherPlayer.name || otherPlayerId.substr(0, 8), otherScreenX, otherScreenY - 30);
      //   ctx.fillText(otherPlayer.name || otherPlayerId.substr(0, 8), otherScreenX, otherScreenY - 30);
      //   
      //   // HP bar for other player
      //   const hpBarW = 40;
      //   const hpBarH = 4;
      //   ctx.fillStyle = '#2c3e50';
      //   ctx.fillRect(otherScreenX - 20, otherScreenY - 35, hpBarW, hpBarH);
      //   ctx.fillStyle = '#2ecc71';
      //   ctx.fillRect(otherScreenX - 20, otherScreenY - 35, hpBarW * (otherPlayer.health / otherPlayer.maxHealth), hpBarH);
      // });
      
      if (game.player.invincible) {
        ctx.save();
        ctx.globalAlpha = 0.5 + Math.sin(Date.now() / 100) * 0.3;
        ctx.strokeStyle = '#ffff00';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.arc(screenPlayerX, screenPlayerY, game.player.size + 10, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
        
        ctx.font = 'bold 12px Arial';
        ctx.fillStyle = '#ffff00';
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 3;
        ctx.textAlign = 'center';
        const timeLeft = Math.ceil((game.player.invincibleUntil - Date.now()) / 1000);
        ctx.strokeText(`🛡️ INVINCIBLE ${timeLeft}s`, screenPlayerX, screenPlayerY - game.player.size - 55);
        ctx.fillText(`🛡️ INVINCIBLE ${timeLeft}s`, screenPlayerX, screenPlayerY - game.player.size - 55);
      }
      
      if (passiveIncome > 0) {
        ctx.font = 'bold 12px Arial';
        ctx.fillStyle = '#00ff00';
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 3;
        ctx.textAlign = 'center';
        ctx.strokeText(`💰 +${passiveIncome}/s`, screenPlayerX, screenPlayerY + game.player.size + 35);
        ctx.fillText(`💰 +${passiveIncome}/s`, screenPlayerX, screenPlayerY + game.player.size + 35);
      }
      
      // Bloodlust stacks indicator
      if (game.player.bloodlust && game.player.bloodlustStacks > 0) {
        ctx.font = 'bold 14px Arial';
        ctx.fillStyle = '#ff0000';
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 3;
        ctx.textAlign = 'center';
        ctx.strokeText(`💀 x${game.player.bloodlustStacks}`, screenPlayerX, screenPlayerY + game.player.size + 50);
        ctx.fillText(`💀 x${game.player.bloodlustStacks}`, screenPlayerX, screenPlayerY + game.player.size + 50);
      }
      
      // Ghost bullets indicator
      if (game.player.ghostBullets) {
        ctx.font = 'bold 10px Arial';
        ctx.fillStyle = '#00ffff';
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.textAlign = 'center';
        ctx.strokeText('👻', screenPlayerX - game.player.size - 15, screenPlayerY);
        ctx.fillText('👻', screenPlayerX - game.player.size - 15, screenPlayerY);
      }

      // UI Overlay
      ctx.fillStyle = 'rgba(15, 20, 35, 0.95)';
      ctx.fillRect(0, 0, canvas.width, 80);
      
      ctx.strokeStyle = '#4ecca3';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(0, 80);
      ctx.lineTo(canvas.width, 80);
      ctx.stroke();
      
      // Ad Reward Button (Desktop)
      if (!isMobile) {
        // Manual wave start button (Desktop)
        if (game.bases.length > 0 && 
            !game.waveActive && 
            game.zombies.length === 0 && 
            game.zombiesLeftToSpawn === 0 && 
            waveCountdown === 0 &&
            !game.initialCountdownActive) {
          const waveButtonX = canvas.width / 2 - 75;
          const waveButtonY = canvas.height - 60;
          const waveButtonW = 150;
          const waveButtonH = 40;
          
          // Pulsing effect
          const pulseScale = 1 + Math.sin(Date.now() / 300) * 0.05;
          
          ctx.save();
          ctx.translate(waveButtonX + waveButtonW/2, waveButtonY + waveButtonH/2);
          ctx.scale(pulseScale, pulseScale);
          ctx.translate(-(waveButtonX + waveButtonW/2), -(waveButtonY + waveButtonH/2));
          
          ctx.fillStyle = 'rgba(16, 185, 129, 0.9)';
          ctx.shadowBlur = 20;
          ctx.shadowColor = '#10b981';
          ctx.fillRect(waveButtonX, waveButtonY, waveButtonW, waveButtonH);
          
          ctx.strokeStyle = '#6ee7b7';
          ctx.lineWidth = 3;
          ctx.strokeRect(waveButtonX, waveButtonY, waveButtonW, waveButtonH);
          
          ctx.shadowBlur = 0;
          ctx.fillStyle = '#fff';
          ctx.font = 'bold 18px Arial';
          ctx.textAlign = 'center';
          ctx.fillText(`🌊 START WAVE ${wave}`, waveButtonX + waveButtonW/2, waveButtonY + 26);
          
          ctx.restore();
        }
        
        const adButtonX = canvas.width - 140;
        const adButtonY = 10;
        const adButtonW = 130;
        const adButtonH = 30;
        
        // Check if mouse is over button
        const mouseOverAd = game.mouseX >= adButtonX && game.mouseX <= adButtonX + adButtonW &&
                            game.mouseY >= adButtonY && game.mouseY <= adButtonY + adButtonH;
        
        ctx.fillStyle = mouseOverAd ? 'rgba(245, 158, 11, 0.9)' : 'rgba(234, 88, 12, 0.8)';
        ctx.fillRect(adButtonX, adButtonY, adButtonW, adButtonH);
        
        ctx.strokeStyle = '#fbbf24';
        ctx.lineWidth = 2;
        ctx.strokeRect(adButtonX, adButtonY, adButtonW, adButtonH);
        
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 14px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('📺 FREE COINS', adButtonX + adButtonW/2, adButtonY + 20);
      }
      
      // HP Bar
      const hpBarX = 15;
      const hpBarY = 15;
      const hpBarW = 180;
      const hpBarH = 22;
      
      ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
      ctx.fillRect(hpBarX - 2, hpBarY - 2, hpBarW + 4, hpBarH + 4);
      
      ctx.fillStyle = '#2c3e50';
      ctx.fillRect(hpBarX, hpBarY, hpBarW, hpBarH);
      
      ctx.fillStyle = game.player.health > 50 ? '#2ecc71' : game.player.health > 25 ? '#f39c12' : '#e74c3c';
      ctx.fillRect(hpBarX, hpBarY, hpBarW * (game.player.health / game.player.maxHealth), hpBarH);
      
      // Shield bar overlay
      if (game.player.maxShield > 0 && game.player.shield > 0) {
        ctx.fillStyle = 'rgba(0, 150, 255, 0.7)';
        ctx.fillRect(hpBarX, hpBarY, hpBarW * (game.player.shield / game.player.maxShield), hpBarH);
      }
      
      ctx.strokeStyle = '#ecf0f1';
      ctx.lineWidth = 2;
      ctx.strokeRect(hpBarX, hpBarY, hpBarW, hpBarH);
      
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 13px Arial';
      ctx.textAlign = 'center';
      const hpText = game.player.shield > 0 ? `${Math.floor(game.player.health)}+${Math.floor(game.player.shield)}` : `${Math.floor(game.player.health)} / ${game.player.maxHealth}`;
      ctx.fillText(hpText, hpBarX + hpBarW/2, hpBarY + 16);
      
      // XP Bar
      const xpBarX = 15;
      const xpBarY = 42;
      const xpBarW = 180;
      const xpBarH = 18;
      const xpNeeded = getXpForLevel(level);
      
      ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
      ctx.fillRect(xpBarX - 2, xpBarY - 2, xpBarW + 4, xpBarH + 4);
      
      ctx.fillStyle = '#2c3e50';
      ctx.fillRect(xpBarX, xpBarY, xpBarW, xpBarH);
      
      const xpPercent = Math.min(1, xp / xpNeeded);
      
      // Pulsing effect when close to level up
      if (xpPercent > 0.8) {
        const pulse = Math.sin(Date.now() / 200) * 0.2 + 0.8;
        ctx.shadowBlur = 10 * pulse;
        ctx.shadowColor = '#9b59b6';
      }
      
      ctx.fillStyle = '#9b59b6';
      ctx.fillRect(xpBarX, xpBarY, xpBarW * xpPercent, xpBarH);
      ctx.shadowBlur = 0;
      
      ctx.strokeStyle = '#ecf0f1';
      ctx.lineWidth = 2;
      ctx.strokeRect(xpBarX, xpBarY, xpBarW, xpBarH);
      
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 11px Arial';
      ctx.fillText(`LVL ${level} • ${Math.floor(xp)}/${xpNeeded}`, xpBarX + xpBarW/2, xpBarY + 13);
      
      // "Almost level up!" message
      if (xpPercent > 0.8 && xpPercent < 1) {
        ctx.font = 'bold 10px Arial';
        ctx.fillStyle = '#ffff00';
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.strokeText('Almost there! ⚡', xpBarX + xpBarW/2, xpBarY - 5);
        ctx.fillText('Almost there! ⚡', xpBarX + xpBarW/2, xpBarY - 5);
      }
      
      // Stats
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 14px Arial';
      ctx.textAlign = 'left';
      ctx.fillText(`Wave ${wave}`, 230, 25);
      ctx.fillText(`Score ${score}`, 230, 45);
      ctx.fillText(`💰 ${coins}`, 360, 25);
      if (passiveIncome > 0) {
        ctx.fillStyle = '#00ff00';
        ctx.fillText(`+${passiveIncome}/s`, 430, 25);
        ctx.fillStyle = '#fff';
      }
      ctx.fillText(`🧟 ${game.zombies.length + game.zombiesLeftToSpawn}`, 360, 45);
      
      ctx.fillText(`🔫 ${game.turrets.length}`, 480, 25);
      ctx.fillText(`🧱 ${game.walls.length}`, 480, 45);
      
      // Active effects display
      let effectsX = 590;
      if (game.player.scavenger) {
        ctx.fillStyle = '#ffd700';
        ctx.fillText('💰', effectsX, 25);
        effectsX += 25;
      }
      if (game.player.chain) {
        ctx.fillStyle = '#00ffff';
        ctx.fillText('⚡', effectsX, 25);
        effectsX += 25;
      }
      if (game.player.ghostBullets) {
        ctx.fillStyle = '#a0a0ff';
        ctx.fillText('👻', effectsX, 25);
        effectsX += 25;
      }
      if (game.player.fortify > 0) {
        ctx.fillStyle = '#4169e1';
        ctx.fillText(`🛡️x${Math.floor(game.player.fortify / 0.2)}`, effectsX, 25);
        effectsX += 35;
      }
      if (game.player.lucky) {
        ctx.fillStyle = '#00ff00';
        ctx.fillText('🍀', effectsX, 25);
        effectsX += 25;
      }
      if (game.player.secondChance && !game.player.secondChanceUsed) {
        ctx.fillStyle = '#ffff00';
        ctx.fillText('💫', effectsX, 25);
        effectsX += 25;
      }
      if (game.player.thorns > 0) {
        ctx.fillStyle = '#ff6600';
        ctx.fillText('🌵', effectsX, 25);
        effectsX += 25;
      }
      if (game.player.timeWarp) {
        ctx.fillStyle = '#9966ff';
        ctx.fillText('⏰', effectsX, 25);
        effectsX += 25;
      }
      if (game.player.xpBoost > 1) {
        ctx.fillStyle = '#ffcc00';
        ctx.fillText(`⭐x${game.player.xpBoost.toFixed(1)}`, effectsX, 25);
        effectsX += 45;
      }
      ctx.fillStyle = '#fff';
      
      // Wave preview
      if (!game.waveActive && game.zombies.length === 0 && game.zombiesLeftToSpawn === 0 && game.bases.length > 0) {
        const previewX = canvas.width - 180;
        const previewY = 80;
        
        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.fillRect(previewX, previewY, 170, 70);
        
        ctx.strokeStyle = '#4ecca3';
        ctx.lineWidth = 2;
        ctx.strokeRect(previewX, previewY, 170, 70);
        
        ctx.font = 'bold 12px Arial';
        ctx.fillStyle = '#4ecca3';
        ctx.textAlign = 'center';
        ctx.fillText('📋 NEXT WAVE', previewX + 85, previewY + 15);
        
        ctx.font = 'bold 11px Arial';
        ctx.fillStyle = '#fff';
        ctx.textAlign = 'left';
        ctx.fillText(`Zombies: ${game.wavePreview.zombieCount}`, previewX + 10, previewY + 35);
        
        const diffColor = game.wavePreview.difficulty === 'Easy' ? '#00ff00' : 
                          game.wavePreview.difficulty === 'Medium' ? '#ffaa00' : 
                          game.wavePreview.difficulty === 'Hard' ? '#ff5500' : '#ff0000';
        ctx.fillStyle = diffColor;
        ctx.fillText(`Difficulty: ${game.wavePreview.difficulty}`, previewX + 10, previewY + 50);
        
        ctx.fillStyle = '#aaa';
        ctx.font = '10px Arial';
        const typesText = game.wavePreview.types.slice(0, 3).join(', ');
        ctx.fillText(`Types: ${typesText}...`, previewX + 10, previewY + 65);
      }
      
      // Wave cooldown
      if (!game.waveActive && game.zombies.length === 0 && game.zombiesLeftToSpawn === 0 && game.bases.length > 0 && game.nextWaveTime) {
        const timeLeft = Math.max(0, Math.ceil((game.nextWaveTime - Date.now()) / 1000));
        if (timeLeft > 0) {
          ctx.font = 'bold 20px Arial';
          ctx.textAlign = 'center';
          ctx.fillStyle = '#00ff00';
          ctx.strokeStyle = '#000';
          ctx.lineWidth = 3;
          const cooldownText = `⏱️ Next Wave in ${timeLeft}s`;
          ctx.strokeText(cooldownText, canvas.width / 2, 90);
          ctx.fillText(cooldownText, canvas.width / 2, 90);
        }
      }
      
      const fireRateDisplay = Math.round(1000 / game.player.fireRate * 10) / 10;
      ctx.fillText(`🔥 ${fireRateDisplay}/s`, 570, 25);
            // Warning if no base / countdown display
      if (game.bases.length === 0 && !game.waveActive) {
        ctx.font = 'bold 18px Arial';
        ctx.textAlign = 'center';
        ctx.fillStyle = '#ff0000';
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 3;
        const warningText = '⚠️ PLACE BASE TO START';
        ctx.strokeText(warningText, canvas.width / 2, 110);
        ctx.fillText(warningText, canvas.width / 2, 110);
        
        ctx.font = 'bold 14px Arial';
        ctx.fillStyle = '#ffff00';
        const helpText = 'Press N → Base (🏠) → Click Map';
        ctx.strokeText(helpText, canvas.width / 2, 135);
        ctx.fillText(helpText, canvas.width / 2, 135);
        
        // Show player ID for multiplayer debugging
        ctx.font = '10px Arial';
        ctx.fillStyle = '#888';
        ctx.strokeText(`Player ID: ${playerId.substr(0, 15)}...`, canvas.width / 2, 155);
        ctx.fillText(`Player ID: ${playerId.substr(0, 15)}...`, canvas.width / 2, 155);
      } else if (waveCountdown > 0) {
        // Show countdown after base is placed
        const pulseScale = 1 + Math.sin(Date.now() / 150) * 0.1;
        ctx.font = `bold ${Math.floor(80 * pulseScale)}px Arial`;
        ctx.textAlign = 'center';
        ctx.fillStyle = waveCountdown <= 3 ? '#ff0000' : '#00ff00';
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 6;
        ctx.shadowBlur = 20;
        ctx.shadowColor = waveCountdown <= 3 ? '#ff0000' : '#00ff00';
        ctx.strokeText(waveCountdown, canvas.width / 2, canvas.height / 2 - 50);
        ctx.fillText(waveCountdown, canvas.width / 2, canvas.height / 2 - 50);
        ctx.shadowBlur = 0;
        
        ctx.font = 'bold 24px Arial';
        ctx.fillStyle = '#ffffff';
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 4;
        const countdownText = waveCountdown <= 3 ? '🚨 GET READY! 🚨' : '⏳ Prepare Your Defenses';
        ctx.strokeText(countdownText, canvas.width / 2, canvas.height / 2 + 20);
        ctx.fillText(countdownText, canvas.width / 2, canvas.height / 2 + 20);
        
        ctx.font = 'bold 16px Arial';
        ctx.fillStyle = '#ffff00';
        const tipText = 'Build walls and turrets now!';
        ctx.strokeText(tipText, canvas.width / 2, canvas.height / 2 + 50);
        ctx.fillText(tipText, canvas.width / 2, canvas.height / 2 + 50);
      } else if (game.bases.length > 0 && game.walls.length === 0 && !game.waveActive) {
        ctx.font = 'bold 14px Arial';
        ctx.textAlign = 'center';
        ctx.fillStyle = '#00ffff';
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 3;
        const tipText = '💡 TIP: Build walls around your base for protection!';
        ctx.strokeText(tipText, canvas.width / 2, 110);
        ctx.fillText(tipText, canvas.width / 2, 110);
        
        ctx.font = 'bold 12px Arial';
        ctx.fillStyle = '#ffffff';
        const tipText2 = 'Zombies will attack walls first if they block their path';
        ctx.strokeText(tipText2, canvas.width / 2, 130);
        ctx.fillText(tipText2, canvas.width / 2, 130);
      } else if (game.bases.length > 0 && 
                 !game.waveActive && 
                 game.zombies.length === 0 && 
                 game.zombiesLeftToSpawn === 0 && 
                 !game.nextWaveTime && 
                 waveCountdown === 0 &&
                 !game.initialCountdownActive) {
        // Show message when wave should start but hasn't
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.fillStyle = '#10b981';
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 3;
        const readyText = '✅ Ready for Next Wave!';
        ctx.strokeText(readyText, canvas.width / 2, 110);
        ctx.fillText(readyText, canvas.width / 2, 110);
        
        if (!isMobile) {
          ctx.font = 'bold 14px Arial';
          ctx.fillStyle = '#6ee7b7';
          const clickText = '👇 Click the button below or wait for auto-start';
          ctx.strokeText(clickText, canvas.width / 2, 135);
          ctx.fillText(clickText, canvas.width / 2, 135);
        }
      }
      
      // Critical base health warning
      if (game.bases.length > 0) {
        const base = game.bases[0];
        const healthPercent = base.health / base.maxHealth;
        if (healthPercent < 0.3) {
          const pulseAlpha = 0.5 + Math.sin(Date.now() / 200) * 0.5;
          ctx.globalAlpha = pulseAlpha;
          ctx.font = 'bold 24px Arial';
          ctx.textAlign = 'center';
          ctx.fillStyle = '#ff0000';
          ctx.strokeStyle = '#000';
          ctx.lineWidth = 4;
          const warningText = '🚨 BASE CRITICAL! 🚨';
          ctx.strokeText(warningText, canvas.width / 2, canvas.height / 2 - 100);
          ctx.fillText(warningText, canvas.width / 2, canvas.height / 2 - 100);
          ctx.globalAlpha = 1;
        }
      }

      // Minimap
      const minimapSize = 150;
      const minimapX = canvas.width - minimapSize - 15;
      const minimapY = canvas.height - minimapSize - 15;
      const scaleX = minimapSize / game.mapWidth;
      const scaleY = minimapSize / game.mapHeight;
      
      ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
      ctx.fillRect(minimapX - 2, minimapY - 2, minimapSize + 4, minimapSize + 4);
      
      ctx.fillStyle = 'rgba(30, 35, 50, 0.8)';
      ctx.fillRect(minimapX, minimapY, minimapSize, minimapSize);
      
      game.walls.forEach(wall => {
        ctx.fillStyle = wall.color || '#95a5a6';
        ctx.fillRect(
          minimapX + wall.x * scaleX,
          minimapY + wall.y * scaleY,
          Math.max(2, wall.width * scaleX),
          Math.max(2, wall.height * scaleY)
        );
      });
      
      game.turrets.forEach(turret => {
        ctx.fillStyle = turret.color || '#3498db';
        ctx.fillRect(
          minimapX + turret.x * scaleX,
          minimapY + turret.y * scaleY,
          4, 4
        );
      });
      
      game.bases.forEach(base => {
        ctx.fillStyle = '#f39c12';
        ctx.shadowBlur = 3;
        ctx.shadowColor = '#f39c12';
        ctx.fillRect(
          minimapX + base.x * scaleX,
          minimapY + base.y * scaleY,
          6, 6
        );
        ctx.shadowBlur = 0;
      });
      
      game.zombies.forEach(zombie => {
        ctx.fillStyle = zombie.color;
        ctx.beginPath();
        ctx.arc(
          minimapX + zombie.x * scaleX,
          minimapY + zombie.y * scaleY,
          3, 0, Math.PI * 2
        );
        ctx.fill();
      });
      
      ctx.fillStyle = '#e74c3c';
      ctx.shadowBlur = 5;
      ctx.shadowColor = '#e74c3c';
      ctx.beginPath();
      ctx.arc(
        minimapX + game.player.x * scaleX,
        minimapY + game.player.y * scaleY,
        4, 0, Math.PI * 2
      );
      ctx.fill();
      ctx.shadowBlur = 0;
      
      ctx.strokeStyle = 'rgba(78, 204, 163, 0.5)';
      ctx.lineWidth = 2;
      ctx.strokeRect(
        minimapX + game.cameraX * scaleX,
        minimapY + game.cameraY * scaleY,
        canvas.width * scaleX,
        canvas.height * scaleY
      );
      
      // Dash indicator (PC)
      if (!isMobile && game.player.dashCooldown > 0) {
        const dashReady = Date.now() - game.player.lastDash >= game.player.dashCooldown * 1000;
        const dashX = 15;
        const dashY = canvas.height - 45;
        
        ctx.fillStyle = dashReady ? 'rgba(46, 204, 113, 0.9)' : 'rgba(231, 76, 60, 0.9)';
        ctx.fillRect(dashX, dashY, 100, 30);
        
        ctx.strokeStyle = '#ecf0f1';
        ctx.lineWidth = 2;
        ctx.strokeRect(dashX, dashY, 100, 30);
        
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('DASH (SPACE)', dashX + 50, dashY + 20);
      }

      // Mobile joystick
      if (isMobile && game.joystick.active) {
        const baseX = game.joystick.startX;
        const baseY = game.joystick.startY;
        const stickX = game.joystick.currentX;
        const stickY = game.joystick.currentY;
        
        ctx.globalAlpha = 0.5;
        ctx.fillStyle = '#4a5568';
        ctx.beginPath();
        ctx.arc(baseX, baseY, 60, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.fillStyle = '#e74c3c';
        ctx.beginPath();
        ctx.arc(stickX, stickY, 35, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1;
      }

      // Mobile aim indicator
      if (isMobile && game.shootTouch.active) {
        const aimX = game.shootTouch.x;
        const aimY = game.shootTouch.y;
        
        ctx.globalAlpha = 0.7;
        ctx.strokeStyle = '#ff0000';
        ctx.lineWidth = 3;
        
        ctx.beginPath();
        ctx.moveTo(aimX - 20, aimY);
        ctx.lineTo(aimX - 5, aimY);
        ctx.moveTo(aimX + 5, aimY);
        ctx.lineTo(aimX + 20, aimY);
        ctx.moveTo(aimX, aimY - 20);
        ctx.lineTo(aimX, aimY - 5);
        ctx.moveTo(aimX, aimY + 5);
        ctx.lineTo(aimX, aimY + 20);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.arc(aimX, aimY, 25, 0, Math.PI * 2);
        ctx.stroke();
        
        ctx.globalAlpha = 1;
      }

      // Mobile control divider
      if (isMobile && gameState === 'playing') {
        const midX = canvas.width / 2;
        ctx.strokeStyle = 'rgba(78, 204, 163, 0.3)';
        ctx.lineWidth = 2;
        ctx.setLineDash([10, 10]);
        ctx.beginPath();
        ctx.moveTo(midX, 0);
        ctx.lineTo(midX, canvas.height);
        ctx.stroke();
        ctx.setLineDash([]);
        
        ctx.globalAlpha = 0.5;
        ctx.fillStyle = '#4ecca3';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('MOVE', midX / 2, canvas.height - 20);
        ctx.fillText('AIM', midX + midX / 2, canvas.height - 20);
        ctx.globalAlpha = 1;
        
        const now = Date.now();
        const timeSinceShot = now - game.lastShot;
        const cooldownPercent = Math.min(1, timeSinceShot / game.player.fireRate);
        
        if (cooldownPercent < 1) {
          const barWidth = 150;
          const barHeight = 8;
          const barX = canvas.width - 175;
          const barY = 70;
          
          ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
          ctx.fillRect(barX - 2, barY - 2, barWidth + 4, barHeight + 4);
          
          ctx.fillStyle = '#e74c3c';
          ctx.fillRect(barX, barY, barWidth, barHeight);
          
          ctx.fillStyle = '#2ecc71';
          ctx.fillRect(barX, barY, barWidth * cooldownPercent, barHeight);
          
          ctx.strokeStyle = '#ecf0f1';
          ctx.lineWidth = 2;
          ctx.strokeRect(barX, barY, barWidth, barHeight);
        }
      }

      animationId = requestAnimationFrame(gameLoop);
      
      // Restore canvas after screen shake
      if (screenShake.intensity > 0) {
        ctx.restore();
      }
    };

    const handleKeyDown = (e) => {
      gameRef.current.keys[e.key] = true;
      
      if (e.key === ' ' && gameRef.current.player.dashCooldown > 0) {
        e.preventDefault();
        performDash();
      }
      
      if (e.key.toLowerCase() === 'b') {
        setShowShop(s => !s);
        gameRef.current.isPaused = !gameRef.current.isPaused;
      }
      
      if (e.key.toLowerCase() === 'n') {
        setShowBuildMenu(s => !s);
      }
      
      if (e.key === 'Escape') {
        if (selectedBuild) {
          setSelectedBuild(null);
          setWallRotation(0);
        } else {
          setShowPauseMenu(s => !s);
          gameRef.current.isPaused = !gameRef.current.isPaused;
        }
        setShowBuildMenu(false);
      }
      
      if (e.key.toLowerCase() === 'r' && selectedBuild) {
        e.preventDefault();
        gameRef.current.rotationFlash = 30;
        setWallRotation(r => {
          const newRotation = (r + 90) % 360;
          console.log('🔄 ROTATION! New angle:', newRotation, '°');
          return newRotation;
        });
      }
      
      if (e.key.toLowerCase() === 't') {
        setShowStats(s => !s);
      }
      
      if (e.key.toLowerCase() === 'q') {
        setShowRanges(s => !s);
      }
      
      const keyNum = parseInt(e.key);
      if (keyNum >= 1 && keyNum <= 9 && !showShop && !showLevelUp && !showUpgradeMenu) {
        e.preventDefault();
        const buildIndex = keyNum - 1;
        if (buildIndex < buildItems.length) {
          const item = buildItems[buildIndex];
          if (coins >= item.cost) {
            setSelectedBuild(item.id);
            setShowBuildMenu(false);
          }
        }
      }
    };

    const handleKeyUp = (e) => {
      gameRef.current.keys[e.key] = false;
    };

    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      gameRef.current.mouseX = e.clientX - rect.left;
      gameRef.current.mouseY = e.clientY - rect.top;
    };

    const handleMouseDown = (e) => {
      const game = gameRef.current;
      const canvas = canvasRef.current;
      if (!canvas) return;
      
      const rect = canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;
      
      // Check manual wave start button (desktop)
      if (!isMobile && gameState === 'playing' && !selectedBuild && 
          game.bases.length > 0 && 
          !game.waveActive && 
          game.zombies.length === 0 && 
          game.zombiesLeftToSpawn === 0 && 
          waveCountdown === 0 &&
          !game.initialCountdownActive) {
        const waveButtonX = canvas.width / 2 - 75;
        const waveButtonY = canvas.height - 60;
        const waveButtonW = 150;
        const waveButtonH = 40;
        
        if (mouseX >= waveButtonX && mouseX <= waveButtonX + waveButtonW &&
            mouseY >= waveButtonY && mouseY <= waveButtonY + waveButtonH) {
          console.log('🎮 Manual wave start triggered (desktop)');
          if (startWaveRef.current) {
            startWaveRef.current(wave);
          }
          return;
        }
      }
      
      // Check ad button click (desktop)
      if (!isMobile && gameState === 'playing' && !selectedBuild) {
        const adButtonX = canvas.width - 140;
        const adButtonY = 10;
        const adButtonW = 130;
        const adButtonH = 30;
        
        if (mouseX >= adButtonX && mouseX <= adButtonX + adButtonW &&
            mouseY >= adButtonY && mouseY <= adButtonY + adButtonH) {
          showAdForReward('coins');
          return;
        }
      }
      
      const worldX = mouseX + game.cameraX;
      const worldY = mouseY + game.cameraY;
      
      if (selectedBuild && gameState === 'playing') {
        e.preventDefault();
        e.stopPropagation();
        
        const item = buildItems.find(b => b.id === selectedBuild);
        if (!item) return;
        
        if (coins < item.cost) {
          alert(`Need ${item.cost} coins, you have ${coins}`);
          return;
        }
        
        const gridSize = 50;
        const snappedX = Math.floor(worldX / gridSize) * gridSize;
        const snappedY = Math.floor(worldY / gridSize) * gridSize;
        
        if (item.type === 'base') {
          if (!game.bases) game.bases = [];
          if (game.bases.length > 0) {
            alert('You can only place one base!');
            setSelectedBuild(null);
            return;
          }
          
          const overlapCheck = checkStructureOverlap(snappedX, snappedY, 100, 100, 'base');
          if (!overlapCheck.valid) {
            alert(`Cannot place base: ${overlapCheck.reason}`);
            return;
          }
        }
        
        if (item.type === 'turret') {
          const overlapCheck = checkStructureOverlap(snappedX, snappedY, 50, 50, 'turret');
          if (!overlapCheck.valid) {
            alert(`Cannot place turret: ${overlapCheck.reason}`);
            return;
          }
        } else if (item.type === 'wall') {
          const currentRotation = wallRotation;
          const isHorizontal = currentRotation % 180 === 0;
          const w = isHorizontal ? 100 : 50;
          const h = isHorizontal ? 50 : 100;
          
          const overlapCheck = checkStructureOverlap(snappedX, snappedY, w, h, 'wall');
          if (!overlapCheck.valid) {
            alert(`Cannot place wall: ${overlapCheck.reason}`);
            return;
          }
        }
        
        setCoins(c => c - item.cost);
        gameRef.current.stats.structuresBuilt++;
        
        if (item.type === 'turret') {
          const newTurret = {
            id: `turret_${Date.now()}_${Math.random()}`,
            builtBy: game.playerId,
            x: snappedX,
            y: snappedY,
            size: 50,
            range: item.stats.range,
            damage: item.stats.damage,
            fireRate: item.stats.fireRate,
            special: item.stats.special,
            cooldown: 0,
            turretType: selectedBuild,
            color: item.color,
            health: 50,
            maxHealth: 50,
            upgradeLevel: 0,
            killCount: 0
          };
          game.turrets.push(newTurret);
          
        } else if (item.type === 'wall') {
          const currentRotation = wallRotation;
          const isHorizontal = currentRotation % 180 === 0;
          
          const newWall = {
            id: `wall_${Date.now()}_${Math.random()}`,
            builtBy: game.playerId,
            x: snappedX,
            y: snappedY,
            width: isHorizontal ? 100 : 50,
            height: isHorizontal ? 50 : 100,
            rotation: currentRotation * Math.PI / 180,
            health: item.stats.health,
            maxHealth: item.stats.maxHealth,
            armor: item.stats.armor,
            tier: item.stats.tier,
            color: item.color,
            icon: item.icon,
            name: 'Wood Wall',
            upgradeLevel: 0
          };
          game.walls.push(newWall);
          
          setWallRotation(0);
        } else if (item.type === 'trap') {
          const newTrap = {
            id: `trap_${Date.now()}_${Math.random()}`,
            builtBy: game.playerId,
            x: snappedX + 25,
            y: snappedY + 25,
            cooldown: 0
          };
          game.traps.push(newTrap);
          
        } else if (item.type === 'base') {
          if (!game.bases) game.bases = [];
          const newBase = {
            id: `base_${Date.now()}_${Math.random()}`,
            builtBy: game.playerId,
            x: snappedX,
            y: snappedY,
            size: 100,
            health: 500 + (baseUpgradeLevel * 100),
            maxHealth: 500 + (baseUpgradeLevel * 100),
            armor: baseUpgradeLevel
          };
          game.bases.push(newBase);
          
          // Visual feedback - particle explosion
          createParticles(snappedX + 50, snappedY + 50, '#f39c12', 30);
          createParticles(snappedX + 50, snappedY + 50, '#ffff00', 20);
          
          // Start countdown before first wave
          game.initialCountdownActive = true;
          setWaveCountdown(15);
          const countdownInterval = setInterval(() => {
            setWaveCountdown(prev => {
              if (prev <= 1) {
                clearInterval(countdownInterval);
                console.log('⏰ Countdown complete, starting wave 1...');
                game.initialCountdownActive = false;
                setTimeout(() => {
                  if (startWaveRef.current && gameState === 'playing') {
                    startWaveRef.current(wave);
                  }
                }, 100);
                return 0;
              }
              return prev - 1;
            });
          }, 1000);
        }
        
        setSelectedBuild(null);
        return;
      }
      
      if (e.button === 0 && gameState === 'playing' && !selectedBuild) {
        for (const turret of game.turrets) {
          if (worldX >= turret.x && worldX <= turret.x + turret.size &&
              worldY >= turret.y && worldY <= turret.y + turret.size) {
            setSelectedStructure({ type: 'turret', data: turret });
            setShowUpgradeMenu(true);
            return;
          }
        }
        
        for (const wall of game.walls) {
          if (worldX >= wall.x && worldX <= wall.x + wall.width &&
              worldY >= wall.y && worldY <= wall.y + wall.height) {
            setSelectedStructure({ type: 'wall', data: wall });
            setShowUpgradeMenu(true);
            return;
          }
        }
        
        game.mouseDown = true;
      }
    };

    const handleMouseUp = () => {
      gameRef.current.mouseDown = false;
    };

    const handleTouchStart = (e) => {
      const game = gameRef.current;
      const canvas = canvasRef.current;
      if (!canvas) return;

      const rect = canvas.getBoundingClientRect();
      
      for (let touch of e.changedTouches) {
        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;
        
        if (x < canvas.width / 2) {
          if (!game.joystick.active) {
            game.joystick.active = true;
            game.joystick.startX = x;
            game.joystick.startY = y;
            game.joystick.currentX = x;
            game.joystick.currentY = y;
            game.joystick.touchId = touch.identifier;
          }
        } else {
          if (!game.shootTouch.active) {
            game.shootTouch.active = true;
            game.shootTouch.x = x;
            game.shootTouch.y = y;
            game.shootTouch.touchId = touch.identifier;
          }
        }
      }
    };

    const handleTouchMove = (e) => {
      e.preventDefault();
      const game = gameRef.current;
      const canvas = canvasRef.current;
      if (!canvas) return;

      const rect = canvas.getBoundingClientRect();
      
      for (let touch of e.changedTouches) {
        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;
        
        if (game.joystick.active && touch.identifier === game.joystick.touchId) {
          game.joystick.currentX = x;
          game.joystick.currentY = y;
        }
        
        if (game.shootTouch.active && touch.identifier === game.shootTouch.touchId) {
          game.shootTouch.x = x;
          game.shootTouch.y = y;
        }
      }
    };

    const handleTouchEnd = (e) => {
      const game = gameRef.current;
      
      for (let touch of e.changedTouches) {
        if (game.joystick.active && touch.identifier === game.joystick.touchId) {
          game.joystick.active = false;
          game.joystick.touchId = null;
        }
        
        if (game.shootTouch.active && touch.identifier === game.shootTouch.touchId) {
          game.shootTouch.active = false;
          game.shootTouch.touchId = null;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mousedown', handleMouseDown);
    window.addEventListener('mouseup', handleMouseUp);
    
    if (isMobile) {
      canvas.addEventListener('touchstart', handleTouchStart, { passive: false });
      canvas.addEventListener('touchmove', handleTouchMove, { passive: false });
      canvas.addEventListener('touchend', handleTouchEnd);
    }

    gameLoop();

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('mousedown', handleMouseDown);
      window.removeEventListener('mouseup', handleMouseUp);
      
      if (isMobile) {
        canvas.removeEventListener('touchstart', handleTouchStart);
        canvas.removeEventListener('touchmove', handleTouchMove);
        canvas.removeEventListener('touchend', handleTouchEnd);
      }
      
      cancelAnimationFrame(animationId);
    };
  }, [gameState, wave, level, xp, coins, isMobile, selectedBuild, wallRotation, canvasWidth, canvasHeight, passiveIncome, waveCountdown, screenShake, killStreak, maxKillStreak, showRanges, playerId]);

  const startGame = () => {
    const game = gameRef.current;
    
    game.playerId = playerId;
    
    game.player = {
      x: 800, y: 600, size: 20, speed: 4, health: 100, maxHealth: 100,
      damage: 1, fireRate: 500, bulletSpeed: 8, piercing: 0,
      lifeSteal: 0, critChance: 0, critDamage: 1.5, dashCooldown: 0,
      lastDash: 0, dashDistance: 100, rage: 0, maxRage: 100,
      hopperRange: 0, hopperLevel: 0,
      shield: 0, maxShield: 0, regenRate: 0,
      vampire: false, berserker: false, ricochet: 0,
      invincible: false, invincibleUntil: 0,
      chain: false, scavenger: false, fortify: 0, lucky: false,
      ghostBullets: false, bloodlust: false, bloodlustStacks: 0
    };
    
    game.zombies = [];
    game.bullets = [];
    game.particles = [];
    game.turrets = [];
    game.walls = [];
    game.traps = [];
    game.bases = [];
    game.coinDrops = [];
    game.powerUps = [];
    game.waveActive = false;
    game.zombiesLeftToSpawn = 0;
    game.isPaused = false;
    game.needsWaveStart = false;
    game.nextWaveTime = null;
    game.nextWaveTimer = null;
    game.lastIncomeTime = Date.now();
    game.initialCountdownActive = false;
    game.stats = {
      zombiesKilled: 0,
      bulletsShot: 0,
      structuresBuilt: 0,
      coinsEarned: 0,
      turretKills: 0,
      wallsDestroyed: 0
    };
    game.wavePreview = {
      zombieCount: 8,
      types: ['normal', 'normal', 'fast'],
      difficulty: 'Easy'
    };
    
    // Center camera on player
    game.cameraX = Math.max(0, Math.min(game.mapWidth - canvasWidth, 800 - canvasWidth/2));
    game.cameraY = Math.max(0, Math.min(game.mapHeight - canvasHeight, 600 - canvasHeight/2));
    
    setWave(1);
    setScore(0);
    setCoins(80); // Reduced from 100
    setTotalCoins(0);
    setXp(0);
    setLevel(1);
    setUpgrades([]);
    setSelectedBuild(null);
    setShowBuildMenu(false);
    setWallRotation(0);
    setSelectedStructure(null);
    setShowUpgradeMenu(false);
    setShowPauseMenu(false);
    setPassiveIncome(0);
    setBaseUpgradeLevel(0);
    setWaveCountdown(0);
    setKillStreak(0);
    setMaxKillStreak(0);
    setCurrentUpgradeOptions([]);
    setPendingLevelUps(0);
    setTotalLevelUps(0);
    setShowRanges(false);
    
    setGameState('playing');
  };

  const getRandomUpgrades = () => {
    const game = gameRef.current;
    const available = upgradeOptions.filter(u => {
      // One-time upgrades that can't be picked again
      if (u.id === 'dash' && game.player.dashCooldown > 0) return false;
      if (u.id === 'multishot' && game.player.multishot) return false;
      if (u.id === 'explosive' && game.player.explosive) return false;
      if (u.id === 'vampire' && game.player.vampire) return false;
      if (u.id === 'berserker' && game.player.berserker) return false;
      if (u.id === 'chain' && game.player.chain) return false;
      if (u.id === 'scavenger' && game.player.scavenger) return false;
      if (u.id === 'lucky' && game.player.lucky) return false;
      if (u.id === 'ghostBullets' && game.player.ghostBullets) return false;
      if (u.id === 'bloodlust' && game.player.bloodlust) return false;
      if (u.id === 'fortify' && game.player.fortify >= 0.6) return false; // Max 3 stacks
      // New advanced upgrades - one-time only
      if (u.id === 'homingShots' && game.player.homingShots) return false;
      if (u.id === 'poisonShots' && game.player.poisonShots) return false;
      if (u.id === 'freezeShots' && game.player.freezeShots) return false;
      if (u.id === 'splitShot' && game.player.splitShot) return false;
      if (u.id === 'laserSight' && game.player.laserSight) return false;
      if (u.id === 'doubleTap' && game.player.doubleTap) return false;
      if (u.id === 'clusterBomb' && game.player.clusterBomb) return false;
      if (u.id === 'lightning' && game.player.lightning) return false;
      if (u.id === 'orbital' && game.player.orbital) return false;
      if (u.id === 'secondChance' && game.player.secondChance) return false;
      if (u.id === 'adrenaline' && game.player.adrenaline) return false;
      if (u.id === 'thorns' && game.player.thorns > 0) return false;
      if (u.id === 'phaseShift' && game.player.phaseShift) return false;
      if (u.id === 'criticalAura' && game.player.criticalAura) return false;
      if (u.id === 'timeWarp' && game.player.timeWarp) return false;
      return true;
    });
    
    const shuffled = [...available].sort(() => Math.random() - 0.5);
    return shuffled.slice(0, 3);
  };

  const applyUpgrade = (upgradeId) => {
    const game = gameRef.current;
    
    setUpgrades(u => [...u, upgradeId]);
    
    switch (upgradeId) {
      // Basic upgrades
      case 'damage':
        game.player.damage += 1;
        break;
      case 'fireRate':
        game.player.fireRate = Math.max(50, game.player.fireRate - 75);
        break;
      case 'health':
        game.player.maxHealth += 25;
        game.player.health += 25;
        break;
      case 'speed':
        game.player.speed += 0.7;
        break;
      case 'piercing':
        game.player.piercing += 1;
        break;
      case 'bulletSpeed':
        game.player.bulletSpeed += 2;
        break;
      case 'lifeSteal':
        game.player.lifeSteal += 0.05;
        break;
      case 'critChance':
        game.player.critChance = Math.min(0.9, game.player.critChance + 0.1);
        break;
      case 'critDamage':
        game.player.critDamage += 0.5;
        break;
      case 'dash':
        game.player.dashCooldown = 3;
        game.player.dashDistance = 120;
        break;
      case 'multishot':
        game.player.multishot = true;
        break;
      case 'explosive':
        game.player.explosive = true;
        break;
      case 'hopper':
        game.player.hopperLevel = (game.player.hopperLevel || 0) + 1;
        game.player.hopperRange = 150 + (game.player.hopperLevel * 50);
        break;
      case 'shield':
        game.player.maxShield += 50;
        game.player.shield = game.player.maxShield;
        break;
      case 'regen':
        game.player.regenRate += 1;
        break;
      case 'vampire':
        game.player.vampire = true;
        break;
      case 'berserker':
        game.player.berserker = true;
        break;
      case 'ricochet':
        game.player.ricochet = 3;
        break;
      case 'chain':
        game.player.chain = true;
        break;
      case 'scavenger':
        game.player.scavenger = true;
        break;
      case 'fortify':
        game.player.fortify = (game.player.fortify || 0) + 0.2;
        break;
      case 'lucky':
        game.player.lucky = true;
        break;
      case 'ghostBullets':
        game.player.ghostBullets = true;
        break;
      case 'bloodlust':
        game.player.bloodlust = true;
        game.player.bloodlustStacks = 0;
        break;
      
      // Advanced shooting upgrades
      case 'homingShots':
        game.player.homingShots = true;
        break;
      case 'poisonShots':
        game.player.poisonShots = true;
        break;
      case 'freezeShots':
        game.player.freezeShots = true;
        break;
      case 'splitShot':
        game.player.splitShot = true;
        break;
      case 'laserSight':
        game.player.laserSight = true;
        game.player.critChance = Math.min(0.9, game.player.critChance + 0.1);
        break;
      case 'doubleTap':
        game.player.doubleTap = true;
        break;
      case 'clusterBomb':
        game.player.clusterBomb = true;
        break;
      case 'lightning':
        game.player.lightning = true;
        break;
      case 'orbital':
        game.player.orbital = true;
        // Initialize 3 orbital bullets
        for (let i = 0; i < 3; i++) {
          game.player.orbitalBullets.push({
            angle: (i / 3) * Math.PI * 2,
            distance: 60
          });
        }
        break;
      
      // Advanced survival upgrades
      case 'secondChance':
        game.player.secondChance = true;
        game.player.secondChanceUsed = false;
        break;
      case 'adrenaline':
        game.player.adrenaline = true;
        break;
      case 'thorns':
        game.player.thorns = 0.3;
        break;
      case 'phaseShift':
        game.player.phaseShift = true;
        break;
      case 'xpBoost':
        game.player.xpBoost = (game.player.xpBoost || 1) + 0.5;
        break;
      case 'criticalAura':
        game.player.criticalAura = true;
        break;
      case 'timeWarp':
        game.player.timeWarp = true;
        break;
    }
    
    // Decrement pending level ups
    setPendingLevelUps(prev => {
      const remaining = prev - 1;
      
      // If more level ups pending, generate new options and keep screen open
      if (remaining > 0) {
        setCurrentUpgradeOptions(getRandomUpgrades());
      } else {
        // No more level ups, close screen and unpause
        setShowLevelUp(false);
        setTotalLevelUps(0);
        game.isPaused = false;
      }
      
      return remaining;
    });
  };

  const buyShopItem = (itemId) => {
    const item = shopItems.find(i => i.id === itemId);
    if (!item || coins < item.cost) return;
    
    // Anti-cheat: Validate purchase
    if (item.cost > coins) {
      console.warn('⚠️ Invalid purchase attempt');
      return;
    }
    
    const game = gameRef.current;
    setCoins(c => Math.max(0, c - item.cost));
    
    switch (itemId) {
      case 'health_potion':
        game.player.health = Math.min(game.player.maxHealth, game.player.health + 50);
        break;
      case 'damage_boost':
        game.player.damage += 2;
        break;
      case 'speed_boost':
        game.player.speed += 1.5;
        break;
      case 'max_health':
        game.player.maxHealth += 50;
        game.player.health += 50;
        break;
      case 'repair_base':
        if (game.bases.length > 0) {
          game.bases[0].health = Math.min(game.bases[0].maxHealth, game.bases[0].health + 100);
        }
        break;
      case 'repair_all':
        game.walls.forEach(wall => {
          wall.health = wall.maxHealth;
        });
        game.turrets.forEach(turret => {
          turret.health = turret.maxHealth;
        });
        break;
      case 'emergency_shield':
        game.player.invincible = true;
        game.player.invincibleUntil = Date.now() + 5000;
        setTimeout(() => {
          game.player.invincible = false;
        }, 5000);
        break;
      case 'nuke':
        game.zombies.forEach(zombie => {
          createParticles(zombie.x, zombie.y, '#ff0000', 20);
          setScore(s => s + zombie.score);
          gameRef.current.stats.zombiesKilled++;
          
          const coinValue = zombie.coins;
          game.coinDrops.push({
            x: zombie.x,
            y: zombie.y,
            value: coinValue,
            lifetime: 300
          });
        });
        game.zombies = [];
        createExplosion(game.player.x, game.player.y, 500, 0);
        break;
      case 'passive_income':
        setPassiveIncome(pi => pi + 1);
        break;
      case 'upgrade_base':
        if (game.bases.length > 0) {
          setBaseUpgradeLevel(l => l + 1);
          game.bases[0].maxHealth += 100;
          game.bases[0].health = game.bases[0].maxHealth;
          game.bases[0].armor = (game.bases[0].armor || 0) + 1;
        }
        break;
    }
  };

  const upgradeTurret = (turret) => {
    const upgradeCost = 60 + (turret.upgradeLevel * 40); // Increased costs
    if (coins < upgradeCost) return;
    
    setCoins(c => c - upgradeCost);
    turret.upgradeLevel++;
    turret.damage *= 1.5;
    turret.range *= 1.2;
    turret.maxHealth += 25;
    turret.health = turret.maxHealth;
    
    setShowUpgradeMenu(false);
    setSelectedStructure(null);
  };

  const showAdForReward = (rewardType) => {
    setAdRewardType(rewardType);
    setAdWatched(false);
    setAdLoading(true);
    setShowAdReward(true);
    
    // Set the correct ad slot based on reward type
    setCurrentAdSlot(adSlots[rewardType] || adSlots.coins);
    
    // Initialize AdSense ad
    setTimeout(() => {
      setAdLoading(false);
      
      // Push the ad to load
      try {
        (window.adsbygoogle = window.adsbygoogle || []).push({});
        console.log(`📺 AdSense ad loaded for ${rewardType} - Slot: ${adSlots[rewardType]}`);
      } catch (e) {
        console.log('⚠️ AdSense error:', e);
      }
      
      // Mark ad as watched after 5 seconds (simulate viewing time)
      setTimeout(() => {
        setAdWatched(true);
        console.log('✅ Ad watched, reward can be claimed');
      }, 5000);
    }, 1000);
  };

  const claimAdReward = () => {
    if (!adWatched) {
      console.log('❌ Cannot claim reward - ad not watched');
      return;
    }
    
    const game = gameRef.current;
    
    // Helper to create particles
    const createParticles = (x, y, color, count) => {
      for (let i = 0; i < count; i++) {
        game.particles.push({
          x, y,
          vx: (Math.random() - 0.5) * 6,
          vy: (Math.random() - 0.5) * 6,
          size: Math.random() * 3 + 2,
          color,
          life: 40,
          alpha: 1,
          rotation: Math.random() * Math.PI * 2,
          rotationSpeed: (Math.random() - 0.5) * 0.2
        });
      }
    };
    
    switch (adRewardType) {
      case 'coins':
        setCoins(c => c + 100);
        setTotalCoins(tc => tc + 100);
        createParticles(game.player.x, game.player.y, '#ffd700', 30);
        break;
      case 'health':
        game.player.health = game.player.maxHealth;
        if (game.bases.length > 0) {
          game.bases[0].health = game.bases[0].maxHealth;
        }
        createParticles(game.player.x, game.player.y, '#ff0000', 25);
        break;
      case 'revive':
        game.player.health = game.player.maxHealth;
        if (game.bases.length > 0 && game.bases[0].health <= 0) {
          game.bases = [{
            x: game.bases[0].x,
            y: game.bases[0].y,
            size: 100,
            health: game.bases[0].maxHealth / 2,
            maxHealth: game.bases[0].maxHealth,
            armor: game.bases[0].armor || 0
          }];
        }
        // Clear some zombies to give player a chance
        game.zombies = game.zombies.slice(0, Math.floor(game.zombies.length / 3));
        setGameState('playing');
        game.isPaused = false;
        createParticles(game.player.x, game.player.y, '#00ff00', 40);
        break;
      case 'powerup':
        game.player.damage += 3;
        game.player.speed += 1;
        createParticles(game.player.x, game.player.y, '#9b59b6', 35);
        setTimeout(() => {
          game.player.damage -= 3;
          game.player.speed -= 1;
        }, 30000); // 30 seconds
        break;
      case 'nuke':
        game.zombies.forEach(zombie => {
          createParticles(zombie.x, zombie.y, '#ff0000', 20);
          setScore(s => s + zombie.score);
          gameRef.current.stats.zombiesKilled++;
        });
        game.zombies = [];
        if (gameState === 'gameover') {
          setGameState('playing');
          game.isPaused = false;
        }
        break;
    }
    
    setShowAdReward(false);
    setAdRewardType(null);
    setAdWatched(false);
    setAdLoading(false);
    setCurrentAdSlot(null);
  };

  const upgradeWall = (wall) => {
    const upgradeCost = 35 + (wall.upgradeLevel * 25); // Increased costs
    if (coins < upgradeCost) return;
    
    setCoins(c => c - upgradeCost);
    wall.upgradeLevel++;
    
    wall.maxHealth = Math.floor(wall.maxHealth * 1.5);
    wall.health = wall.maxHealth;
    wall.armor = Math.min(5, (wall.armor || 0) + 1);
    
    if (wall.upgradeLevel === 2 && wall.tier === 1) {
      wall.tier = 2;
      wall.color = '#95a5a6';
      wall.icon = '🧱';
      wall.name = 'Stone Wall';
    } else if (wall.upgradeLevel === 4 && wall.tier === 2) {
      wall.tier = 3;
      wall.color = '#7f8c8d';
      wall.icon = '🔩';
      wall.name = 'Metal Wall';
    }
    
    setShowUpgradeMenu(false);
    setSelectedStructure(null);
  };

  const sellStructure = (structure, type) => {
    const game = gameRef.current;
    const refund = type === 'turret' ? 20 : type === 'wall' ? 8 : 0; // Reduced refunds
    
    setCoins(c => c + refund);
    
    if (type === 'turret') {
      game.turrets = game.turrets.filter(t => t !== structure);
    } else if (type === 'wall') {
      game.walls = game.walls.filter(w => w !== structure);
    }
    
    setShowUpgradeMenu(false);
    setSelectedStructure(null);
  };

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-black">
      {/* Header */}
      <header className="bg-black/90 border-b-4 border-cyan-500 shadow-lg sticky top-0 z-50">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between flex-wrap gap-4">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 md:h-12 md:w-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center text-2xl md:text-3xl shadow-lg">
                🎮
              </div>
              <div>
                <h1 className="text-xl md:text-2xl font-bold text-cyan-400">LetUsTech</h1>
                <p className="text-xs text-gray-400 hidden md:block">Zombie Survival Game</p>
              </div>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden text-cyan-400 text-2xl p-2 hover:bg-cyan-400/20 rounded-lg transition"
            >
              {mobileMenuOpen ? '✖️' : '☰'}
            </button>

            {/* Navigation - Desktop */}
            <nav className="hidden md:flex items-center gap-6">
              <a href="/index.html" className="text-white hover:text-cyan-400 transition font-semibold">🏠 Home</a>
              <a href="/index.html#about" className="text-white hover:text-cyan-400 transition font-semibold">📖 About</a>
              <a href="/index.html#programs" className="text-white hover:text-cyan-400 transition font-semibold">💻 Programs</a>
              <a href="/index.html#games" className="text-white hover:text-cyan-400 transition font-semibold">🎮 Games</a>
              <a 
                href="https://www.paypal.com/donate/?hosted_button_id=MJNXEL8GRRPSL" 
                target="_blank"
                rel="noopener noreferrer"
                className="bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-white px-4 py-2 rounded-lg font-bold transition transform hover:scale-105"
              >
                💝 Donate
              </a>
            </nav>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <nav className="md:hidden mt-4 pb-2 space-y-2 border-t border-cyan-500/30 pt-4">
              <a 
                href="/index.html" 
                onClick={() => setMobileMenuOpen(false)}
                className="block text-white hover:text-cyan-400 transition font-semibold py-2"
              >
                🏠 Home
              </a>
              <a 
                href="/index.html#about" 
                onClick={() => setMobileMenuOpen(false)}
                className="block text-white hover:text-cyan-400 transition font-semibold py-2"
              >
                📖 About
              </a>
              <a 
                href="/index.html#programs" 
                onClick={() => setMobileMenuOpen(false)}
                className="block text-white hover:text-cyan-400 transition font-semibold py-2"
              >
                💻 Programs
              </a>
              <a 
                href="/index.html#games" 
                onClick={() => setMobileMenuOpen(false)}
                className="block text-white hover:text-cyan-400 transition font-semibold py-2"
              >
                🎮 Games
              </a>
              <a 
                href="https://www.paypal.com/donate/?hosted_button_id=MJNXEL8GRRPSL" 
                target="_blank"
                rel="noopener noreferrer"
                className="block bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-white px-4 py-2 rounded-lg font-bold transition text-center"
              >
                💝 Donate
              </a>
            </nav>
          )}
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center p-4">
      
      {/* Top Display Ad */}
      {gameState === 'playing' && (
        <div className="w-full max-w-6xl mb-4 bg-black/50 rounded-lg p-2 border-2 border-cyan-500/30">
          <div className="text-center">
            <p className="text-xs text-gray-400 mb-1">Advertisement</p>
            <ins className="adsbygoogle"
                 style={{ display: 'block' }}
                 data-ad-client="ca-pub-5830581574523106"
                 data-ad-slot="1636874707"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
          </div>
        </div>
      )}
      
      {gameState === 'menu' && (
        <div className="bg-black/80 rounded-xl p-8 border-4 border-cyan-500 text-center max-w-2xl">
          <h1 className="text-5xl md:text-7xl font-bold text-cyan-400 mb-2">LetUsTech</h1>
          <h2 className="text-4xl md:text-6xl font-bold text-red-500 mb-4">ZOMBIE SURVIVAL! 🧟</h2>
          <p className="text-2xl md:text-3xl text-white mb-8">🏠 Defend Your Base! 💥</p>
          <div className="text-left text-white mb-6 space-y-2 bg-black/50 p-4 rounded">
            <p className="text-lg md:text-xl font-bold mb-2 text-cyan-400">🎮 Controls:</p>
            <p className="ml-4">• WASD / Arrows - Move</p>
            <p className="ml-4">• Mouse - Aim & Shoot</p>
            <p className="ml-4">• Space - Dash (unlock)</p>
            <p className="ml-4">• N - Build Menu (or press 1-9 for quick build)</p>
            <p className="ml-4">• R - Rotate Walls</p>
            <p className="ml-4">• B - Shop</p>
            <p className="ml-4">• Q - Toggle Ranges (Base safe zone & Turret ranges)</p>
            <p className="ml-4">• ESC - Pause</p>
            <p className="ml-4">• T - Stats</p>
            <p className="ml-4 text-cyan-300">👻 You can walk through walls!</p>
            <p className="ml-4 text-green-300">🔫 Turrets can be placed adjacent to anything!</p>
            <p className="ml-4 text-purple-400">💎 <span className="font-bold">Kill zombies to gain XP and level up!</span></p>
          </div>
          <div className="text-left text-white mb-6 space-y-2 bg-black/50 p-4 rounded">
            <p className="text-lg md:text-xl font-bold mb-2 text-yellow-400">✨ Features:</p>
            <p className="ml-4 text-purple-400">• 🎨 <span className="font-bold">Enhanced Graphics!</span> - Detailed models for all units, textured walls, animated effects!</p>
            <p className="ml-4 text-red-400">• 🧟 <span className="font-bold">17 Zombie Types!</span> - Each with unique visual design and abilities!</p>
            <p className="ml-4 text-green-400">• 💚 <span className="font-bold">Active Healers!</span> - Healer zombies ACTUALLY heal nearby zombies with visual effects!</p>
            <p className="ml-4 text-cyan-400">• ⚡ <span className="font-bold">Faster Movement!</span> - Improved player speed (5.5 base) & zombie speeds for better gameplay!</p>
            <p className="ml-4 text-orange-400">• 🎯 <span className="font-bold">40+ UPGRADES!</span> - Homing bullets, poison, freeze, orbital, laser sight, double tap & MORE!</p>
            <p className="ml-4 text-pink-400">• 🔫 <span className="font-bold">Advanced Shooting!</span> - Split shots, cluster bombs, lightning strikes, time warp!</p>
            <p className="ml-4 text-cyan-400">• 🏗️ <span className="font-bold">Detailed Models!</span> - Armored player, 5 turret types, textured walls (wood/stone/metal), 3D fortress base!</p>
            <p className="ml-4 text-yellow-400">• 💫 <span className="font-bold">Survival Abilities!</span> - Second Chance, Adrenaline Rush, Thorns, Phase Shift!</p>
            <p className="ml-4 text-green-400">• 🎁 <span className="font-bold">Power-Up Drops!</span> - Health, Speed, Damage, Fire Rate, Coins (10% drop chance)</p>
            <p className="ml-4 text-orange-400">• 🔥 <span className="font-bold">Kill Streak System!</span> - +10 coins every 10 kills, streak timer resets after 3s</p>
            <p className="ml-4 text-blue-400">• 🏗️ <span className="font-bold">Flexible Building!</span> - Place turrets adjacent to walls, base & other turrets</p>
            <p className="ml-4 text-yellow-400">• 🛒 <span className="font-bold">Enhanced Shop!</span> - Smooth horizontal scrolling (mouse wheel supported!)</p>
            <p className="ml-4 text-cyan-400">• 👁️ <span className="font-bold">Range Toggle (Q)</span> - View turret ranges and base safe zones on demand</p>
            <p className="ml-4 text-pink-400">• 📺 <span className="font-bold">Ad Rewards!</span> - Watch ads completely to earn rewards (5s simulation)</p>
            <p className="ml-4 text-green-400">• 🌊 <span className="font-bold">Manual Wave Start!</span> - Button appears if waves get stuck</p>
          </div>
          <div className="text-left text-white mb-6 space-y-2 bg-black/50 p-4 rounded">
            <p className="text-lg md:text-xl font-bold mb-2 text-red-400">🧟 Zombie Types:</p>
            <p className="ml-4 text-sm"><span className="font-bold text-green-400">Normal</span> - Standard zombie (Faster!)</p>
            <p className="ml-4 text-sm"><span className="font-bold text-red-400">Fast</span> - Quick but weak (Even faster!)</p>
            <p className="ml-4 text-sm"><span className="font-bold text-blue-400">Tank</span> - Slow but tough</p>
            <p className="ml-4 text-sm"><span className="font-bold text-orange-400">Exploder</span> - Explodes on death (Faster!)</p>
            <p className="ml-4 text-sm"><span className="font-bold text-green-400">Healer ✚</span> - ACTIVELY heals nearby zombies with visual beams!</p>
            <p className="ml-4 text-sm"><span className="font-bold text-orange-400">Splitter ⚡</span> - Splits into 2 fast zombies (Faster!)</p>
            <p className="ml-4 text-sm"><span className="font-bold text-gray-400">Armored</span> - High armor, damage reduction</p>
            <p className="ml-4 text-sm"><span className="font-bold text-red-400">Berserker</span> - Gets faster when damaged (Faster!)</p>
            <p className="ml-4 text-sm"><span className="font-bold text-purple-400">Necromancer ☠️</span> - Summons minions (Faster!)</p>
            <p className="ml-4 text-sm"><span className="font-bold text-teal-400">Shielded 🛡️</span> - Has protective shield (Faster!)</p>
            <p className="ml-4 text-sm"><span className="font-bold text-purple-600">Boss</span> - High HP, appears wave 5+ (Faster!)</p>
            <p className="ml-4 text-sm"><span className="font-bold text-red-600">Megaboss</span> - Massive HP, wave 15+ (Faster!)</p>
            <p className="ml-4 text-sm"><span className="font-bold text-pink-500">Sprinter ⚡</span> - Ultra fast, low HP (NEW!)</p>
            <p className="ml-4 text-sm"><span className="font-bold text-gray-600">Juggernaut 🛡️</span> - Slow tank, massive HP (NEW!)</p>
            <p className="ml-4 text-sm"><span className="font-bold text-lime-400">Toxic ☢️</span> - Poison cloud damage (NEW!)</p>
            <p className="ml-4 text-sm"><span className="font-bold text-fuchsia-500">Teleporter 🌀</span> - Blinks around (NEW!)</p>
            <p className="ml-4 text-sm"><span className="font-bold text-red-800">Vampire 🩸</span> - Steals life from attacks (NEW!)</p>
          </div>
          {highScore > 0 && (
            <p className="text-xl text-yellow-400 mb-4">🏆 High Score: {highScore}</p>
          )}
                      <p className="text-sm text-gray-400 mb-4 italic">
            💡 Watch ads completely (5s) for rewards! Wave countdown prevents early spawns.
          </p>
          <button 
            onClick={startGame}
            className="px-12 py-4 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white text-3xl font-bold rounded-xl transition transform hover:scale-110 shadow-lg"
          >
            ▶️ START GAME
          </button>
          <p className="text-xs text-gray-500 mt-4">© LetUsTech - Zombie Survival Game</p>
        </div>
      )}

      <div className="relative">
        <canvas 
          ref={canvasRef} 
          width={canvasWidth} 
          height={canvasHeight}
          className="border-4 border-cyan-500 rounded-lg shadow-2xl"
        />
        
        {/* Mobile controls */}
        {isMobile && gameState === 'playing' && (
          <div className="absolute bottom-4 right-4 flex flex-col gap-2">
            {/* Manual wave start button */}
            {gameRef.current.bases.length > 0 && 
             !gameRef.current.waveActive && 
             gameRef.current.zombies.length === 0 && 
             gameRef.current.zombiesLeftToSpawn === 0 && 
             waveCountdown === 0 &&
             !gameRef.current.initialCountdownActive && (
              <button
                onClick={() => {
                  console.log('🎮 Manual wave start triggered');
                  if (startWaveRef.current) {
                    startWaveRef.current(wave);
                  }
                }}
                className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 rounded-lg shadow-lg flex items-center justify-center text-2xl font-bold border-2 border-green-300 animate-pulse"
              >
                🌊
              </button>
            )}
            <button
              onClick={() => setShowBuildMenu(s => !s)}
              className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 rounded-lg shadow-lg flex items-center justify-center text-3xl font-bold border-2 border-blue-300"
            >
              🔨
            </button>
            {gameRef.current.player.dashCooldown > 0 && (
              <button
                onClick={performDash}
                disabled={Date.now() - gameRef.current.player.lastDash < gameRef.current.player.dashCooldown * 1000}
                className="w-16 h-16 bg-gradient-to-br from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 disabled:bg-gray-500 disabled:opacity-50 rounded-lg shadow-lg flex items-center justify-center text-3xl font-bold border-2 border-cyan-300"
              >
                ⚡
              </button>
            )}
            <button
              onClick={() => showAdForReward('coins')}
              className="w-16 h-16 bg-gradient-to-br from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 rounded-lg shadow-lg flex items-center justify-center text-2xl font-bold border-2 border-yellow-300"
            >
              📺
            </button>
          </div>
        )}
        
        {/* Build menu */}
        {showBuildMenu && !showShop && !showLevelUp && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-black/95 via-blue-900/90 to-black/95 rounded-xl backdrop-blur-sm p-4 z-40">
            <div className="text-center mb-6">
              <h3 className="text-4xl md:text-6xl font-bold text-cyan-400 mb-2 drop-shadow-lg">🔨 BUILD MENU</h3>
              <div className="flex items-center justify-center gap-3 mb-2">
                <div className="text-xl md:text-2xl text-white">Your Coins:</div>
                <div className="text-2xl md:text-4xl text-yellow-400 font-bold bg-black/50 px-4 py-2 rounded-lg border-2 border-yellow-500">
                  💰 {coins}
                </div>
              </div>
              <p className="text-sm md:text-base text-cyan-400">
                {isMobile ? '← Scroll to browse → Tap item then tap map' : '← Scroll (mouse wheel) or press 1-9 → Click item then map'}
              </p>
            </div>
            
            <div className="relative w-full max-w-6xl mb-6">
              {/* Scroll container */}
              <div ref={buildScrollRef} className="overflow-x-auto overflow-y-hidden pb-4 px-4 scrollbar-build">
                <div className="flex gap-4 min-w-max">
                  {buildItems.map((item, index) => (
                    <button
                      key={item.id}
                      onClick={() => {
                        if (coins >= item.cost) {
                          setSelectedBuild(item.id);
                          setShowBuildMenu(false);
                        }
                      }}
                      disabled={coins < item.cost}
                      className={`${
                        coins >= item.cost 
                          ? 'bg-gradient-to-br from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 hover:scale-105 hover:shadow-2xl' 
                          : 'bg-gray-700 cursor-not-allowed opacity-60'
                      } border-4 ${item.type === 'base' ? 'border-orange-500' : item.type === 'turret' ? 'border-blue-400' : item.type === 'wall' ? 'border-gray-400' : 'border-red-400'} p-5 rounded-xl w-64 transition transform shadow-xl flex-shrink-0 relative overflow-hidden`}
                    >
                      {/* Hotkey badge for PC */}
                      {!isMobile && index < 9 && (
                        <div className="absolute top-2 left-2 bg-yellow-500 text-black font-bold text-sm px-2 py-1 rounded-lg shadow-lg z-20">
                          {index + 1}
                        </div>
                      )}
                      
                      {/* Shine effect */}
                      {coins >= item.cost && (
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent transform -skew-x-12 translate-x-full hover:translate-x-[-200%] transition-transform duration-1000"></div>
                      )}
                      
                      <div className="relative z-10">
                        <div className="text-6xl mb-3 drop-shadow-lg">{item.icon}</div>
                        <h4 className="text-white font-bold text-xl mb-2">{item.name}</h4>
                        <p className="text-gray-200 text-sm mb-3 min-h-[60px]">{item.desc}</p>
                        
                        {/* Stats display for turrets */}
                        {item.type === 'turret' && item.stats && (
                          <div className="bg-black/40 p-2 rounded-lg mb-3 text-left text-xs">
                            <div className="text-red-400">⚔️ Damage: {item.stats.damage}</div>
                            <div className="text-blue-400">🎯 Range: {item.stats.range}</div>
                            <div className="text-green-400">⚡ Rate: {Math.round(60 / item.stats.fireRate * 10) / 10}/s</div>
                            {item.stats.special !== 'none' && (
                              <div className="text-purple-400">✨ {item.stats.special}</div>
                            )}
                          </div>
                        )}
                        
                        {/* Cost display */}
                        <div className={`flex items-center justify-center gap-2 ${item.cost === 0 ? 'bg-green-600/40' : 'bg-black/40'} py-2 px-3 rounded-lg`}>
                          {item.cost === 0 ? (
                            <span className="text-green-300 font-bold text-xl">FREE!</span>
                          ) : (
                            <>
                              <span className="text-yellow-300 font-bold text-2xl">{item.cost}</span>
                              <span className="text-yellow-400 text-xl">💰</span>
                            </>
                          )}
                        </div>
                        
                        {coins < item.cost && item.cost > 0 && (
                          <div className="mt-2 text-red-400 text-xs font-bold">
                            Need {item.cost - coins} more coins
                          </div>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Scroll indicators */}
              <div className="absolute left-0 top-0 bottom-0 w-12 bg-gradient-to-r from-black/60 to-transparent pointer-events-none rounded-l-xl"></div>
              <div className="absolute right-0 top-0 bottom-0 w-12 bg-gradient-to-l from-black/60 to-transparent pointer-events-none rounded-r-xl"></div>
            </div>
            
            <button
              onClick={() => setShowBuildMenu(false)}
              className="px-8 py-3 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white text-xl font-bold rounded-xl transition transform hover:scale-110 shadow-lg border-2 border-red-400"
            >
              ✖️ CLOSE BUILD MENU
            </button>
            
            <style jsx>{`
              .scrollbar-build {
                scroll-behavior: smooth;
              }
              .scrollbar-build::-webkit-scrollbar {
                height: 12px;
              }
              .scrollbar-build::-webkit-scrollbar-track {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
              }
              .scrollbar-build::-webkit-scrollbar-thumb {
                background: linear-gradient(90deg, #3498db, #2980b9);
                border-radius: 10px;
                border: 2px solid rgba(0, 0, 0, 0.3);
              }
              .scrollbar-build::-webkit-scrollbar-thumb:hover {
                background: linear-gradient(90deg, #2980b9, #1f618d);
              }
            `}</style>
          </div>
        )}
        
        {/* Shop */}
        {showShop && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-black/95 via-purple-900/90 to-black/95 rounded-xl backdrop-blur-sm p-4 z-40">
            <div className="text-center mb-6">
              <h2 className="text-4xl md:text-6xl font-bold text-yellow-400 mb-2 drop-shadow-lg">🛒 SHOP</h2>
              <div className="flex items-center justify-center gap-3 mb-2">
                <div className="text-xl md:text-2xl text-white">Your Coins:</div>
                <div className="text-2xl md:text-4xl text-yellow-400 font-bold bg-black/50 px-4 py-2 rounded-lg border-2 border-yellow-500">
                  💰 {coins}
                </div>
              </div>
              <p className="text-sm md:text-base text-cyan-400">← Scroll horizontally to browse → (Use mouse wheel)</p>
            </div>
            
            <div className="relative w-full max-w-6xl mb-6">
              {/* Scroll container */}
              <div ref={shopScrollRef} className="overflow-x-auto overflow-y-hidden pb-4 px-4 scrollbar-custom">
                <div className="flex gap-4 min-w-max">
                  {shopItems.map(item => (
                    <button
                      key={item.id}
                      onClick={() => buyShopItem(item.id)}
                      disabled={coins < item.cost}
                      className={`${
                        coins >= item.cost 
                          ? 'bg-gradient-to-br from-yellow-600 to-orange-600 hover:from-yellow-700 hover:to-orange-700 hover:scale-105 hover:shadow-2xl' 
                          : 'bg-gray-700 cursor-not-allowed opacity-60'
                      } border-4 border-yellow-500 p-5 rounded-xl w-64 transition transform shadow-xl flex-shrink-0 relative overflow-hidden`}
                    >
                      {/* Shine effect */}
                      {coins >= item.cost && (
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent transform -skew-x-12 translate-x-full hover:translate-x-[-200%] transition-transform duration-1000"></div>
                      )}
                      
                      <div className="relative z-10">
                        <div className="text-6xl mb-3 drop-shadow-lg">{item.icon}</div>
                        <h3 className="text-white font-bold text-xl mb-2">{item.name}</h3>
                        <p className="text-gray-200 text-sm mb-3 min-h-[40px]">{item.desc}</p>
                        <div className="flex items-center justify-center gap-2 bg-black/40 py-2 px-3 rounded-lg">
                          <span className="text-yellow-300 font-bold text-2xl">{item.cost}</span>
                          <span className="text-yellow-400 text-xl">💰</span>
                        </div>
                        {coins < item.cost && (
                          <div className="mt-2 text-red-400 text-xs font-bold">
                            Need {item.cost - coins} more coins
                          </div>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Scroll indicators */}
              <div className="absolute left-0 top-0 bottom-0 w-12 bg-gradient-to-r from-black/60 to-transparent pointer-events-none rounded-l-xl"></div>
              <div className="absolute right-0 top-0 bottom-0 w-12 bg-gradient-to-l from-black/60 to-transparent pointer-events-none rounded-r-xl"></div>
            </div>
            
            <button
              onClick={() => {
                setShowShop(false);
                gameRef.current.isPaused = false;
              }}
              className="px-8 py-3 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white text-xl font-bold rounded-xl transition transform hover:scale-110 shadow-lg border-2 border-red-400"
            >
              ✖️ CLOSE SHOP
            </button>
            
            <style jsx>{`
              .scrollbar-custom {
                scroll-behavior: smooth;
              }
              .scrollbar-custom::-webkit-scrollbar {
                height: 12px;
              }
              .scrollbar-custom::-webkit-scrollbar-track {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
              }
              .scrollbar-custom::-webkit-scrollbar-thumb {
                background: linear-gradient(90deg, #f39c12, #e67e22);
                border-radius: 10px;
                border: 2px solid rgba(0, 0, 0, 0.3);
              }
              .scrollbar-custom::-webkit-scrollbar-thumb:hover {
                background: linear-gradient(90deg, #e67e22, #d35400);
              }
            `}</style>
          </div>
        )}
        
        {/* Level up */}
        {showLevelUp && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-black/95 to-purple-900/95 rounded-xl backdrop-blur-sm p-4 overflow-y-auto z-50">
            <div className="text-center mb-6 animate-pulse">
              <h2 className="text-5xl md:text-7xl font-bold text-yellow-400 mb-3 drop-shadow-lg">⬆️ LEVEL UP!</h2>
              <p className="text-2xl md:text-3xl text-cyan-400 mb-2">You reached Level {level}! 🎉</p>
            </div>
            {totalLevelUps > 1 && (
              <p className="text-lg md:text-xl text-cyan-400 mb-2 font-bold">
                🎁 Upgrade {totalLevelUps - pendingLevelUps + 1} of {totalLevelUps}
              </p>
            )}
            {pendingLevelUps > 1 && (
              <p className="text-base md:text-lg text-green-400 mb-2">
                ✨ {pendingLevelUps - 1} more {pendingLevelUps - 1 === 1 ? 'upgrade' : 'upgrades'} after this!
              </p>
            )}
            <p className="text-xl md:text-2xl text-white mb-2">Choose Your Upgrade:</p>
            <p className="text-sm text-gray-400 mb-6">Kill zombies to gain XP and level up!</p>
            <div className="flex flex-col md:flex-row gap-4 md:gap-5 mb-4">
              {currentUpgradeOptions.map(upgrade => (
                <button
                  key={upgrade.id}
                  onClick={() => applyUpgrade(upgrade.id)}
                  className="bg-gradient-to-br from-gray-800 to-gray-900 hover:from-purple-700 hover:to-purple-800 border-4 border-yellow-500 hover:border-yellow-300 p-5 md:p-6 rounded-xl w-full md:w-52 transition-all transform hover:scale-110 shadow-2xl hover:shadow-yellow-500/50"
                >
                  <div className="text-5xl md:text-6xl mb-3 animate-bounce">{upgrade.icon}</div>
                  <h3 className="text-white font-bold text-lg md:text-xl mb-2">{upgrade.name}</h3>
                  <p className="text-gray-300 text-sm">{upgrade.desc}</p>
                </button>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-2">💡 Tip: Each upgrade makes you stronger! Choose wisely based on your playstyle.</p>
          </div>
        )}
        
        {/* Upgrade menu */}
        {showUpgradeMenu && selectedStructure && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/90 rounded-xl backdrop-blur-sm p-4 z-40">
            <div className="bg-gradient-to-br from-gray-800 to-gray-900 p-6 rounded-xl border-4 border-cyan-500 max-w-md">
              <h2 className="text-3xl font-bold text-cyan-400 mb-4">
                {selectedStructure.type === 'turret' ? '🔫 Turret Menu' : 
                 selectedStructure.data.tier === 1 ? '🪵 Wood Wall Menu' :
                 selectedStructure.data.tier === 2 ? '🧱 Stone Wall Menu' :
                 selectedStructure.data.tier === 3 ? '🔩 Metal Wall Menu' : '🧱 Wall Menu'}
              </h2>
              
              {selectedStructure.type === 'turret' && (
                <>
                  <div className="text-white mb-4 space-y-2">
                    <p className="text-lg">Level: <span className="text-yellow-400 font-bold">★{selectedStructure.data.upgradeLevel}</span></p>
                    <p className="text-lg">Damage: <span className="text-red-400 font-bold">{selectedStructure.data.damage.toFixed(1)}</span></p>
                    <p className="text-lg">Range: <span className="text-blue-400 font-bold">{selectedStructure.data.range.toFixed(0)}</span></p>
                    <p className="text-lg">Health: <span className="text-green-400 font-bold">{Math.floor(selectedStructure.data.health)}/{selectedStructure.data.maxHealth}</span></p>
                  </div>
                  <button
                    onClick={() => upgradeTurret(selectedStructure.data)}
                    disabled={coins < 60 + (selectedStructure.data.upgradeLevel * 40)}
                    className="w-full mb-2 px-4 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold rounded-lg transition"
                  >
                    ⬆️ Upgrade ({60 + (selectedStructure.data.upgradeLevel * 40)} coins)
                  </button>
                </>
              )}
              
              {selectedStructure.type === 'wall' && (
                <>
                  <div className="text-white mb-4 space-y-2">
                    <p className="text-lg">Level: <span className="text-yellow-400 font-bold">★{selectedStructure.data.upgradeLevel}</span></p>
                    <p className="text-lg">Tier: <span className="text-purple-400 font-bold">{
                      selectedStructure.data.tier === 1 ? '🪵 Wood' : 
                      selectedStructure.data.tier === 2 ? '🧱 Stone' : 
                      selectedStructure.data.tier === 3 ? '🔩 Metal' : 'Max'
                    }</span></p>
                    <p className="text-lg">Health: <span className="text-green-400 font-bold">{Math.floor(selectedStructure.data.health)}/{selectedStructure.data.maxHealth}</span></p>
                    <p className="text-lg">Armor: <span className="text-blue-400 font-bold">🛡️ {selectedStructure.data.armor}</span></p>
                    {selectedStructure.data.upgradeLevel === 1 && <p className="text-sm text-yellow-300 italic">Next: Upgrade to Stone Wall</p>}
                    {selectedStructure.data.upgradeLevel === 3 && <p className="text-sm text-yellow-300 italic">Next: Upgrade to Metal Wall</p>}
                  </div>
                  <button
                    onClick={() => upgradeWall(selectedStructure.data)}
                    disabled={coins < 35 + (selectedStructure.data.upgradeLevel * 25)}
                    className="w-full mb-2 px-4 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold rounded-lg transition"
                  >
                    ⬆️ Upgrade ({35 + (selectedStructure.data.upgradeLevel * 25)} coins)
                  </button>
                </>
              )}
              
              <button
                onClick={() => sellStructure(selectedStructure.data, selectedStructure.type)}
                className="w-full mb-2 px-4 py-3 bg-orange-600 hover:bg-orange-700 text-white font-bold rounded-lg transition"
              >
                💰 Sell ({selectedStructure.type === 'turret' ? 20 : 8} coins)
              </button>
              <button
                onClick={() => {
                  setShowUpgradeMenu(false);
                  setSelectedStructure(null);
                }}
                className="w-full px-4 py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded-lg transition"
              >
                Close
              </button>
            </div>
          </div>
        )}
        
        {/* Pause menu */}
        {showPauseMenu && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/90 rounded-xl backdrop-blur-sm p-4 z-50">
            <div className="bg-gradient-to-br from-gray-800 to-gray-900 p-8 rounded-xl border-4 border-cyan-500 max-w-md text-center">
              <h2 className="text-4xl font-bold text-cyan-400 mb-2">⏸️ PAUSED</h2>
              <p className="text-sm text-gray-400 mb-6">LetUsTech Zombie Survival!</p>
              <div className="space-y-3">
                <button
                  onClick={() => {
                    setShowPauseMenu(false);
                    gameRef.current.isPaused = false;
                  }}
                  className="w-full px-6 py-3 bg-green-600 hover:bg-green-700 text-white text-xl font-bold rounded-lg"
                >
                  ▶️ Resume
                </button>
                <button
                  onClick={() => setShowStats(s => !s)}
                  className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white text-xl font-bold rounded-lg"
                >
                  📊 Stats
                </button>
                <button
                  onClick={() => showAdForReward('coins')}
                  className="w-full px-6 py-3 bg-gradient-to-r from-yellow-600 to-orange-600 hover:from-yellow-700 hover:to-orange-700 text-white text-xl font-bold rounded-lg border-2 border-yellow-400"
                >
                  📺 Watch Ad → +100 💰
                </button>
                <button
                  onClick={() => showAdForReward('health')}
                  className="w-full px-6 py-3 bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700 text-white text-xl font-bold rounded-lg border-2 border-red-400"
                >
                  📺 Watch Ad → Full HP ❤️
                </button>
                <button
                  onClick={() => showAdForReward('powerup')}
                  className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white text-xl font-bold rounded-lg border-2 border-purple-400"
                >
                  📺 Watch Ad → 30s Boost ⚡
                </button>
                <button
                  onClick={() => {
                    setShowPauseMenu(false);
                    setGameState('menu');
                  }}
                  className="w-full px-6 py-3 bg-red-600 hover:bg-red-700 text-white text-xl font-bold rounded-lg"
                >
                  🏠 Main Menu
                </button>
              </div>
            </div>
          </div>
        )}
        
        {/* Stats panel */}
        {showStats && (
          <div className="absolute top-20 left-4 bg-black/95 rounded-xl p-4 border-2 border-yellow-500 max-w-xs z-30">
            <h3 className="text-xl font-bold text-yellow-400 mb-3 text-center">📊 STATS</h3>
            <div className="text-white space-y-1 text-sm">
              <p>🧟 Zombies Killed: <span className="text-green-400">{gameRef.current.stats.zombiesKilled}</span></p>
              <p>💥 Bullets Shot: <span className="text-orange-400">{gameRef.current.stats.bulletsShot}</span></p>
              <p>🔨 Structures Built: <span className="text-blue-400">{gameRef.current.stats.structuresBuilt}</span></p>
              <p>💰 Coins Earned: <span className="text-yellow-400">{gameRef.current.stats.coinsEarned}</span></p>
              <p>🎯 Turret Kills: <span className="text-purple-400">{Math.floor(gameRef.current.stats.turretKills)}</span></p>
              <p>💔 Walls Destroyed: <span className="text-red-400">{gameRef.current.stats.wallsDestroyed}</span></p>
            </div>
            <button
              onClick={() => setShowStats(false)}
              className="w-full mt-3 px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-bold rounded-lg"
            >
              Close
            </button>
          </div>
        )}
        
        {/* Game over */}
        {gameState === 'gameover' && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-black/95 to-red-900/95 rounded-xl backdrop-blur-sm p-4 overflow-y-auto z-50">
            <h1 className="text-5xl md:text-7xl font-bold text-red-600 mb-2">💀 GAME OVER</h1>
            <p className="text-xl md:text-2xl text-orange-400 mb-4">🏠 Your Base Was Destroyed! 💥</p>
            <p className="text-lg text-cyan-400 mb-4">LetUsTech Zombie Survival!</p>
            <div className="bg-black/50 p-6 md:p-8 rounded-xl border-2 border-red-500 mb-6">
              <p className="text-2xl md:text-3xl text-white mb-2">Wave: <span className="text-cyan-400 font-bold">{wave}</span></p>
              <p className="text-2xl md:text-3xl text-yellow-400 mb-2">Score: <span className="font-bold">{score}</span></p>
              <p className="text-xl md:text-2xl text-green-400 mb-2">Coins: <span className="font-bold">{totalCoins}</span></p>
              <p className="text-xl md:text-2xl text-purple-400 mb-2">Level: <span className="font-bold">{level}</span></p>
              <p className="text-lg text-orange-400 mb-2">Max Streak: <span className="font-bold">🔥 {maxKillStreak}</span></p>
              <p className="text-lg text-gray-300">Zombies Killed: <span className="font-bold">{gameRef.current.stats.zombiesKilled}</span></p>
            </div>
            {score > highScore && score > 0 && (
              <p className="text-xl md:text-2xl text-yellow-300 mb-4">🏆 NEW HIGH SCORE! 🏆</p>
            )}
            
            {/* Ad Reward Options */}
            <div className="bg-gradient-to-br from-purple-900/50 to-blue-900/50 p-4 rounded-xl border-2 border-yellow-400 mb-4">
              <p className="text-yellow-400 font-bold text-lg mb-3">📺 Watch Ads to Continue!</p>
              <div className="space-y-2">
                <button
                  onClick={() => showAdForReward('revive')}
                  className="w-full px-6 py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white text-xl font-bold rounded-xl transition transform hover:scale-105 shadow-lg border-4 border-green-400"
                >
                  📺 Revive & Continue! 🔄
                </button>
                <button
                  onClick={() => showAdForReward('nuke')}
                  className="w-full px-6 py-4 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 text-white text-xl font-bold rounded-xl transition transform hover:scale-105 shadow-lg border-4 border-orange-400"
                >
                  📺 Clear All Zombies! ☢️
                </button>
              </div>
            </div>
            
            <div className="mb-6 text-gray-200 max-w-2xl">
              <p className="text-lg md:text-xl font-bold mb-3 text-cyan-400">Upgrades Collected:</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {upgrades.length > 0 ? upgrades.map((upId, idx) => {
                  const upgrade = upgradeOptions.find(u => u.id === upId);
                  return upgrade ? (
                    <span key={idx} className="bg-gradient-to-r from-gray-700 to-gray-800 px-3 md:px-4 py-2 rounded-lg text-sm md:text-base border border-gray-600">
                      {upgrade.icon} {upgrade.name}
                    </span>
                  ) : null;
                }) : <span className="text-gray-400">No upgrades</span>}
              </div>
            </div>
            <button 
              onClick={startGame}
              className="px-8 md:px-12 py-3 md:py-4 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white text-xl md:text-2xl font-bold rounded-xl transition transform hover:scale-110 shadow-lg"
            >
              🔄 TRY AGAIN
            </button>
          </div>
        )}
              {/* Ad Reward Modal */}
        {showAdReward && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/95 rounded-xl backdrop-blur-sm p-4 z-[60]">
            <div className="bg-gradient-to-br from-purple-900 to-indigo-900 p-8 rounded-xl border-4 border-yellow-400 max-w-lg text-center">
              <h2 className="text-4xl font-bold text-yellow-400 mb-4">📺 Advertisement</h2>
              <p className="text-white text-xl mb-6">
                {adRewardType === 'coins' && '🎁 Watch an ad to earn 100 free coins!'}
                {adRewardType === 'health' && '❤️ Watch an ad to restore full health!'}
                {adRewardType === 'revive' && '🔄 Watch an ad to continue your game!'}
                {adRewardType === 'powerup' && '⚡ Watch an ad for a 30-second power boost!'}
                {adRewardType === 'nuke' && '☢️ Watch an ad to clear all zombies!'}
              </p>
              
              {/* Show current ad slot for debugging */}
              <p className="text-xs text-gray-400 mb-4">Ad Unit: {currentAdSlot}</p>
              
              {/* Ad Placeholder */}
              <div className="bg-gray-800 rounded-lg p-8 mb-6 border-2 border-gray-600 min-h-[200px] flex items-center justify-center">
                <div className="text-center">
                  {adLoading ? (
                    <>
                      <div className="text-6xl mb-4 animate-pulse">📺</div>
                      <p className="text-yellow-400 text-lg mb-2 font-bold">Loading Advertisement...</p>
                      <div className="w-48 h-2 bg-gray-700 rounded-full overflow-hidden mx-auto">
                        <div className="h-full bg-yellow-400 animate-pulse w-1/2"></div>
                      </div>
                    </>
                  ) : adWatched ? (
                    <>
                      <div className="text-6xl mb-4">✅</div>
                      <p className="text-green-400 text-lg mb-2 font-bold">Ad Complete!</p>
                      <p className="text-gray-400 text-sm">You can now claim your reward</p>
                    </>
                  ) : (
                    <>
                      <div className="text-6xl mb-4 animate-bounce">▶️</div>
                      <p className="text-cyan-400 text-lg mb-2 font-bold">Watching Advertisement...</p>
                      <p className="text-gray-400 text-sm">Please wait 5 seconds</p>
                      <div className="mt-4">
                        <ins className="adsbygoogle"
                             style={{ display: 'block' }}
                             data-ad-client="ca-pub-5830581574523106"
                             data-ad-slot={currentAdSlot}
                             data-ad-format="auto"
                             data-full-width-responsive="true"></ins>
                      </div>
                    </>
                  )}
                </div>
              </div>
              
              <div className="space-y-3">
                <button
                  onClick={claimAdReward}
                  disabled={!adWatched}
                  className={`w-full px-8 py-4 ${
                    adWatched 
                      ? 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 cursor-pointer' 
                      : 'bg-gray-600 cursor-not-allowed opacity-50'
                  } text-white text-xl font-bold rounded-xl transition transform hover:scale-105 shadow-lg border-2 ${
                    adWatched ? 'border-green-400' : 'border-gray-500'
                  }`}
                >
                  {adWatched ? '✅ Claim Reward' : '⏳ Waiting for Ad...'}
                </button>
                <button
                  onClick={() => {
                    setShowAdReward(false);
                    setAdRewardType(null);
                    setAdWatched(false);
                    setAdLoading(false);
                    setCurrentAdSlot(null);
                  }}
                  className="w-full px-8 py-4 bg-gray-700 hover:bg-gray-600 text-white text-lg font-bold rounded-xl transition"
                >
                  ❌ Cancel
                </button>
              </div>
              
              <p className="text-gray-400 text-xs mt-4">
                Ads help support free game development!
              </p>
            </div>
          </div>
        )}
        
      </div>
      </div>
      
      {/* Bottom Display Ad */}
      {gameState === 'playing' && (
        <div className="w-full max-w-6xl mx-auto mb-4 bg-black/50 rounded-lg p-2 border-2 border-cyan-500/30">
          <div className="text-center">
            <p className="text-xs text-gray-400 mb-1">Advertisement</p>
            <ins className="adsbygoogle"
                 style={{ display: 'block' }}
                 data-ad-client="ca-pub-5830581574523106"
                 data-ad-slot="1551553723"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="bg-black/90 border-t-4 border-cyan-500 mt-auto">
        <div className="container mx-auto px-4 py-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-4">
            {/* About */}
            <div>
              <h3 className="text-cyan-400 font-bold text-lg mb-2">About LetUsTech</h3>
              <p className="text-gray-300 text-sm mb-2">
                Open-source games and programs created with passion. Join our community!
              </p>
              <p className="text-gray-400 text-sm italic">
                Created by a 23 year old who loves to learn code and make code. Building fun projects and sharing them with the world! 🚀
              </p>
            </div>

            {/* Quick Links */}
            <div>
              <h3 className="text-cyan-400 font-bold text-lg mb-2">Quick Links</h3>
              <div className="space-y-1">
                <a href="/index.html" className="block text-gray-300 hover:text-cyan-400 transition text-sm">🏠 Home</a>
                <a href="/index.html#about" className="block text-gray-300 hover:text-cyan-400 transition text-sm">📖 About</a>
                <a href="/index.html#programs" className="block text-gray-300 hover:text-cyan-400 transition text-sm">💻 Programs</a>
                <a href="/index.html#games" className="block text-gray-300 hover:text-cyan-400 transition text-sm">🎮 Games</a>
              </div>
            </div>

            {/* Support & Contact */}
            <div>
              <h3 className="text-cyan-400 font-bold text-lg mb-2">Support & Contact</h3>
              <div className="space-y-2">
                <a 
                  href="https://discord.gg/dkebMS5eCX" 
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block text-gray-300 hover:text-blue-400 transition text-sm"
                >
                  💡 Feature Request
                </a>
                <a 
                  href="https://www.paypal.com/donate/?hosted_button_id=MJNXEL8GRRPSL" 
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block text-yellow-400 hover:text-yellow-300 transition text-sm font-semibold"
                >
                  💝 Donate via PayPal
                </a>
              </div>
            </div>
          </div>

          {/* Copyright */}
          <div className="border-t border-cyan-500/30 pt-4 text-center">
            <p className="text-gray-400 text-sm">
              © 2024 LetUsTech. Open Source. Made with ❤️ by the community.
            </p>
            <p className="text-gray-500 text-xs mt-1">
              <a 
                href="https://github.com/letustec-oss/LetUsTech" 
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-cyan-400 transition"
              >
                View on GitHub
              </a>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

// ===== MOUNT REACT APP =====
window.addEventListener('load', function() {
  console.log('🚀 Mounting React application...');
  try {
    const rootElement = document.getElementById('root');
    if (!rootElement) {
      throw new Error('Root element #root not found!');
    }

    const root = ReactDOM.createRoot(rootElement);
    root.render(<ZombieWaveGame />);
    console.log('✅ SUCCESS! Game loaded and running!');
  } catch (error) {
    console.error('❌ FATAL ERROR:', error);
  }
});
