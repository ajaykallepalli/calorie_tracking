import React from 'react'
import { Bell, Home, BarChart2, Settings, Plus } from 'lucide-react'
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

export default function FitnessTracker() {
  const totalCalories = 2000
  const caloriesLeft = 1532

  return (
    <div className="max-w-md mx-auto bg-gray-100 min-h-screen">
      <header className="bg-white p-4 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <span className="text-xl font-bold">🍎 Cal AI</span>
        </div>
        <Bell className="w-6 h-6" />
      </header>

      <main className="p-4">
        <div className="flex justify-between mb-4">
          {['T', 'F', 'S', 'S', 'M', 'T', 'W'].map((day, index) => (
            <div key={index} className={`w-8 h-8 flex items-center justify-center rounded-full ${index === 3 ? 'bg-black text-white' : 'bg-white'}`}>
              {day}
            </div>
          ))}
        </div>

        <Card className="mb-4">
          <CardContent className="p-4">
            <div className="flex justify-between items-center mb-2">
              <div>
                <span className="text-3xl font-bold">{caloriesLeft}</span>
                <span className="text-sm text-gray-500"> / {totalCalories}</span>
              </div>
              <Progress value={(caloriesLeft / totalCalories) * 100} className="w-1/2" />
            </div>
            <div className="text-sm text-gray-500">Calories left</div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-3 gap-4 mb-4">
          {[
            { label: 'Protein left', value: '146g', color: 'text-red-500' },
            { label: 'Carbs left', value: '91g', color: 'text-orange-500' },
            { label: 'Fat left', value: '19g', color: 'text-blue-500' },
          ].map((item, index) => (
            <Card key={index}>
              <CardContent className="p-2 text-center">
                <div className={`text-lg font-bold ${item.color}`}>{item.value}</div>
                <div className="text-xs text-gray-500">{item.label}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        <h2 className="text-xl font-bold mb-2">Recently logged</h2>
        {[
          { name: 'Pizza Slices with Yog...', time: '7:50 PM', calories: 500, protein: 20, carbs: 60, fat: 20 },
          { name: 'Waffle with Brown S...', time: '3:31 PM', calories: 450, protein: 6, carbs: 66, fat: 18 },
        ].map((meal, index) => (
          <Card key={index} className="mb-4">
            <CardContent className="p-4 flex items-center space-x-4">
              <div className="w-16 h-16 bg-gray-300 rounded-md"></div>
              <div className="flex-1">
                <h3 className="font-semibold">{meal.name}</h3>
                <p className="text-sm text-gray-500">{meal.time}</p>
                <div className="flex flex-wrap gap-2 text-sm">
                  <span>🔥 {meal.calories} calories</span>
                  <span>🍗 {meal.protein}g</span>
                  <span>🌾 {meal.carbs}g</span>
                  <span>🥑 {meal.fat}g</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </main>

      <footer className="fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around p-2">
        <Button variant="ghost" size="icon">
          <Home className="h-6 w-6" />
        </Button>
        <Button variant="ghost" size="icon">
          <BarChart2 className="h-6 w-6" />
        </Button>
        <Button variant="ghost" size="icon" className="rounded-full bg-black text-white">
          <Plus className="h-6 w-6" />
        </Button>
        <Button variant="ghost" size="icon">
          <Settings className="h-6 w-6" />
        </Button>
      </footer>
    </div>
  )
}