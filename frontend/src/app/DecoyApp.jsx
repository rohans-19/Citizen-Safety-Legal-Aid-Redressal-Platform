import { useState, useEffect } from 'react'

const DAYS       = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const SLOTS      = ['Breakfast', 'Lunch', 'Dinner']
const CATEGORIES = ['All', 'Breakfast', 'Lunch', 'Dinner', 'Snack']

// Color palette for recipe card thumbnails (avoids missing-emoji problem)
const CARD_COLORS = [
  'bg-amber-50', 'bg-orange-50', 'bg-rose-50', 'bg-green-50',
  'bg-teal-50',  'bg-blue-50',   'bg-purple-50', 'bg-yellow-50',
]

export default function DecoyApp() {
  const [activeTab, setActiveTab]         = useState('browse')
  const [recipes, setRecipes]             = useState([])
  const [categoryFilter, setCategoryFilter] = useState('All')
  const [saved, setSaved]                 = useState([1, 5, 8])
  const [planner, setPlanner]             = useState({})
  const [searchQuery, setSearchQuery]     = useState('')

  useEffect(() => {
    fetch('/recipe_data.json')
      .then(r => r.json())
      .then(setRecipes)
      .catch(() => setRecipes([]))
  }, [])

  const filteredRecipes = recipes.filter(r => {
    const matchCat    = categoryFilter === 'All' || r.category === categoryFilter
    const matchSearch = r.name.toLowerCase().includes(searchQuery.toLowerCase())
    return matchCat && matchSearch
  })

  const toggleSave = (id) =>
    setSaved(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id])

  const assignToPlanner = (day, slot, recipeId) =>
    setPlanner(prev => ({ ...prev, [`${day}-${slot}`]: recipeId }))

  const savedRecipes = recipes.filter(r => saved.includes(r.id))

  return (
    <div className="min-h-screen bg-white flex flex-col max-w-md mx-auto">

      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">🍴</span>
            <span className="font-semibold text-gray-800 text-lg">Rasoi</span>
          </div>
          <span className="text-xs text-gray-400">Recipe Companion</span>
        </div>
      </header>

      {/* Tab Navigation */}
      <nav className="bg-white border-b border-gray-200 px-4 sticky top-[57px] z-10">
        <div className="flex">
          {[
            { key: 'browse',  label: 'Browse' },
            { key: 'planner', label: 'Meal Planner' },
            { key: 'saved',   label: `Saved (${saved.length})` },
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`py-3 px-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.key
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      <main className="flex-1 overflow-y-auto">

        {/* === BROWSE TAB === */}
        {activeTab === 'browse' && (
          <div className="p-4 space-y-4 screen-fade">

            {/* Search */}
            <input
              type="text"
              placeholder="Search recipes..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
            />

            {/* Category filter pills */}
            <div className="flex gap-2 overflow-x-auto pb-1 no-select">
              {CATEGORIES.map(cat => (
                <button
                  key={cat}
                  onClick={() => setCategoryFilter(cat)}
                  className={`px-3 py-1 rounded text-xs font-medium whitespace-nowrap border transition-colors ${
                    categoryFilter === cat
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Recipe grid */}
            {filteredRecipes.length === 0 ? (
              <p className="text-center text-gray-400 text-sm py-8">No recipes found.</p>
            ) : (
              <div className="grid grid-cols-2 gap-3">
                {filteredRecipes.map(recipe => (
                  <RecipeCard
                    key={recipe.id}
                    recipe={recipe}
                    isSaved={saved.includes(recipe.id)}
                    onToggleSave={() => toggleSave(recipe.id)}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* === MEAL PLANNER TAB === */}
        {activeTab === 'planner' && (
          <div className="p-4 screen-fade">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold text-gray-700">Weekly Meal Plan</h2>
              <button
                onClick={() => setPlanner({})}
                className="text-xs text-gray-400 hover:text-red-500 border border-gray-200 hover:border-red-300 rounded px-2 py-0.5"
              >
                Clear all
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs border-collapse min-w-[400px]">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="border border-gray-200 px-2 py-2 text-left text-gray-500 font-medium w-12">Day</th>
                    {SLOTS.map(slot => (
                      <th key={slot} className="border border-gray-200 px-2 py-2 text-gray-500 font-medium text-center">{slot}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {DAYS.map(day => (
                    <tr key={day} className="hover:bg-gray-50">
                      <td className="border border-gray-200 px-2 py-2 font-semibold text-gray-600 whitespace-nowrap">{day}</td>
                      {SLOTS.map(slot => {
                        const key = `${day}-${slot}`
                        const assignedId     = planner[key]
                        const assignedRecipe = recipes.find(r => r.id === assignedId)
                        return (
                          <td key={slot} className="border border-gray-200 px-2 py-1">
                            {assignedRecipe ? (
                              <div className="flex items-center gap-1 justify-between">
                                <span className="text-gray-700 truncate max-w-[80px] text-xs">{assignedRecipe.name}</span>
                                <button
                                  onClick={() => assignToPlanner(day, slot, null)}
                                  className="text-gray-300 hover:text-red-400 flex-shrink-0 text-base leading-none"
                                >×</button>
                              </div>
                            ) : (
                              <select
                                className="w-full text-xs text-gray-400 border border-gray-100 bg-white rounded focus:outline-none focus:border-blue-400 cursor-pointer py-1"
                                value=""
                                onChange={e => e.target.value && assignToPlanner(day, slot, parseInt(e.target.value))}
                              >
                                <option value="">+ Add</option>
                                {recipes.map(r => (
                                  <option key={r.id} value={r.id}>{r.name}</option>
                                ))}
                              </select>
                            )}
                          </td>
                        )
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* === SAVED TAB === */}
        {activeTab === 'saved' && (
          <div className="p-4 screen-fade">
            {savedRecipes.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-3xl mb-2">🔖</p>
                <p className="text-gray-500 text-sm">No saved recipes yet.</p>
                <p className="text-gray-400 text-xs mt-1">Tap the star icon on any recipe to save it.</p>
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-xs text-gray-400 mb-3">{savedRecipes.length} saved recipe{savedRecipes.length !== 1 ? 's' : ''}</p>
                {savedRecipes.map(recipe => (
                  <div key={recipe.id} className="flex items-center gap-3 border border-gray-200 rounded-md p-3">
                    {/* Color dot instead of emoji to avoid rendering issues */}
                    <div className={`w-10 h-10 rounded flex items-center justify-center text-lg flex-shrink-0 ${CARD_COLORS[recipe.id % CARD_COLORS.length]}`}>
                      {recipe.emoji}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-800 text-sm">{recipe.name}</p>
                      <p className="text-gray-400 text-xs truncate">{recipe.description}</p>
                    </div>
                    <div className="flex flex-col items-end gap-1 flex-shrink-0">
                      <span className="text-xs text-gray-400">{recipe.time}</span>
                      <button
                        onClick={() => toggleSave(recipe.id)}
                        className="text-xs text-blue-500 hover:text-red-500 font-medium"
                        title="Remove from saved"
                      >
                        ★ Saved
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      <div className="h-4" />
    </div>
  )
}

// Recipe card sub-component
function RecipeCard({ recipe, isSaved, onToggleSave }) {
  const colorClass = CARD_COLORS[(recipe.id - 1) % CARD_COLORS.length]

  return (
    <div className="border border-gray-200 rounded-md overflow-hidden bg-white">
      {/* Color thumbnail with emoji */}
      <div className={`h-20 flex items-center justify-center text-3xl border-b border-gray-100 ${colorClass}`}>
        {recipe.emoji}
      </div>
      <div className="p-2">
        <p className="font-medium text-gray-800 text-xs leading-snug">{recipe.name}</p>
        <div className="flex items-center justify-between mt-1">
          <span className="text-xs text-gray-400">{recipe.time}</span>
          {/* Use ★/☆ for clear visual distinction between saved and unsaved */}
          <button
            onClick={onToggleSave}
            className={`text-sm leading-none ${isSaved ? 'text-blue-500' : 'text-gray-300 hover:text-gray-400'}`}
            title={isSaved ? 'Remove bookmark' : 'Bookmark this recipe'}
          >
            {isSaved ? '★' : '☆'}
          </button>
        </div>
        <span className="inline-block mt-1 text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded">
          {recipe.category}
        </span>
      </div>
    </div>
  )
}
