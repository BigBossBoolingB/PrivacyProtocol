import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Link as LinkIcon, Search } from "lucide-react";
import { motion } from "framer-motion";

export default function URLAnalyzer({ onAnalyze }) {
  const [url, setUrl] = useState('');
  const [title, setTitle] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (url.trim()) {
      onAnalyze(url.trim(), title.trim());
    }
  };

  return (
    <Card className="bg-gray-900/50 border-gray-800/50 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <LinkIcon className="w-5 h-5 text-blue-400" />
          Analyze Privacy Policy URL
        </CardTitle>
      </CardHeader>
      <CardContent>
        <motion.form
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          onSubmit={handleSubmit}
          className="space-y-6"
        >
          <div className="space-y-2">
            <Label htmlFor="url" className="text-white">
              Privacy Policy URL
            </Label>
            <Input
              id="url"
              type="url"
              placeholder="https://example.com/privacy-policy"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="bg-gray-800/50 border-gray-700 text-white placeholder-gray-400"
              required
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="title" className="text-white">
              Service Name (Optional)
            </Label>
            <Input
              id="title"
              type="text"
              placeholder="e.g., Facebook, Google, Amazon"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="bg-gray-800/50 border-gray-700 text-white placeholder-gray-400"
            />
          </div>
          
          <Button
            type="submit"
            className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-medium py-3 rounded-xl"
          >
            <Search className="w-5 h-5 mr-2" />
            Analyze Privacy Policy
          </Button>
        </motion.form>
      </CardContent>
    </Card>
  );
}