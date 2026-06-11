import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { MessageCircle, Smartphone, Mail, Sparkles, CheckCircle } from 'lucide-react'
import { getSegments } from '../api/segments'
import { createCampaign, launchCampaign, aiCampaignMessage } from '../api/campaigns'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Textarea } from '../components/ui/textarea'
import { cn } from '../lib/utils'

const CHANNELS = [
  { id: 'whatsapp', label: 'WhatsApp', icon: MessageCircle, color: 'text-green-600' },
  { id: 'sms', label: 'SMS', icon: Smartphone, color: 'text-blue-600' },
  { id: 'email', label: 'Email', icon: Mail, color: 'text-gray-600' },
]

const STEPS = ['Select Segment', 'Choose Channel', 'Write Message', 'Review & Launch']

export default function CreateCampaign() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [step, setStep] = useState(0)
  const [name, setName] = useState('')
  const [segmentId, setSegmentId] = useState('')
  const [channel, setChannel] = useState('whatsapp')
  const [message, setMessage] = useState('')
  const [campaignId, setCampaignId] = useState(null)
  const [toast, setToast] = useState(null)
  const [aiLoading, setAiLoading] = useState(false)

  const { data: segments = [] } = useQuery({
    queryKey: ['segments'],
    queryFn: getSegments,
  })

  const selectedSegment = segments.find((s) => s.id === Number(segmentId))

  const createMutation = useMutation({
    mutationFn: createCampaign,
    onSuccess: (data) => {
      setCampaignId(data.id)
      setStep(3)
    },
  })

  const launchMutation = useMutation({
    mutationFn: () => launchCampaign(campaignId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] })
      setToast('Campaign launched successfully!')
      setTimeout(() => navigate(`/campaigns/${campaignId}`), 1500)
    },
  })

  const handleAIMessage = async () => {
    if (!campaignId) {
      const draft = await createMutation.mutateAsync({
        name: name || 'Draft Campaign',
        segment_id: Number(segmentId),
        channel,
        message_template: message || 'Draft message',
      })
      setCampaignId(draft.id)
      setAiLoading(true)
      try {
        const { message: aiMsg } = await aiCampaignMessage(draft.id)
        setMessage(aiMsg)
      } finally {
        setAiLoading(false)
      }
      return
    }
    setAiLoading(true)
    try {
      const { message: aiMsg } = await aiCampaignMessage(campaignId)
      setMessage(aiMsg)
    } finally {
      setAiLoading(false)
    }
  }

  const handleLaunch = async () => {
    let id = campaignId
    if (!id) {
      const draft = await createMutation.mutateAsync({
        name,
        segment_id: Number(segmentId),
        channel,
        message_template: message,
      })
      id = draft.id
      setCampaignId(id)
    }
    await launchCampaign(id)
    queryClient.invalidateQueries({ queryKey: ['campaigns'] })
    setToast('Campaign launched successfully!')
    setTimeout(() => navigate(`/campaigns/${id}`), 1500)
  }

  const charLimit = channel === 'sms' ? 160 : 300
  const preview = message.replace('{name}', 'Rahul')

  return (
    <div className="max-w-2xl space-y-6">
      <div className="flex gap-2">
        {STEPS.map((s, i) => (
          <div
            key={s}
            className={cn(
              'flex-1 rounded-lg px-3 py-2 text-center text-xs font-medium transition-colors',
              i === step ? 'bg-primary text-white' : i < step ? 'bg-primary/10 text-primary' : 'bg-gray-100 text-gray-400'
            )}
          >
            {i + 1}. {s}
          </div>
        ))}
      </div>

      {step === 0 && (
        <Card>
          <CardHeader><CardTitle>Step 1: Select Segment</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <Input placeholder="Campaign name" value={name} onChange={(e) => setName(e.target.value)} />
            <select
              className="flex h-10 w-full rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              value={segmentId}
              onChange={(e) => setSegmentId(e.target.value)}
            >
              <option value="">Select a segment...</option>
              {segments.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.customer_count} customers)
                </option>
              ))}
            </select>
            <Button disabled={!segmentId || !name} onClick={() => setStep(1)}>Next</Button>
          </CardContent>
        </Card>
      )}

      {step === 1 && (
        <Card>
          <CardHeader><CardTitle>Step 2: Choose Channel</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-3">
              {CHANNELS.map(({ id, label, icon: Icon, color }) => (
                <button
                  key={id}
                  onClick={() => setChannel(id)}
                  className={cn(
                    'flex flex-col items-center gap-2 rounded-xl border-2 p-4 transition-all hover:shadow-sm',
                    channel === id ? 'border-primary bg-primary/5' : 'border-gray-200'
                  )}
                >
                  <Icon className={cn('h-8 w-8', color)} />
                  <span className="text-sm font-medium">{label}</span>
                </button>
              ))}
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setStep(0)}>Back</Button>
              <Button onClick={() => setStep(2)}>Next</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {step === 2 && (
        <Card>
          <CardHeader><CardTitle>Step 3: Write Message</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              placeholder="Write your message... Use {name} for personalization"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={4}
            />
            <div className="flex items-center justify-between">
              <span className={cn('text-xs', message.length > charLimit ? 'text-red-500' : 'text-gray-400')}>
                {message.length}/{charLimit} characters
              </span>
              <Button variant="outline" size="sm" onClick={handleAIMessage} disabled={aiLoading}>
                <Sparkles className="h-4 w-4 mr-1" />
                {aiLoading ? 'Writing...' : 'Write with AI'}
              </Button>
            </div>
            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-xs font-medium text-gray-500 mb-1">Preview</p>
              <p className="text-sm text-gray-700">{preview || 'Your message preview will appear here'}</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setStep(1)}>Back</Button>
              <Button disabled={!message} onClick={() => setStep(3)}>Next</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {step === 3 && (
        <Card>
          <CardHeader><CardTitle>Step 4: Review & Launch</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-lg border border-gray-200 p-4 space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-gray-500">Campaign</span><span className="font-medium">{name}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Segment</span><span className="font-medium">{selectedSegment?.name}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Recipients</span><span className="font-medium">{selectedSegment?.customer_count} customers</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Channel</span><span className="font-medium capitalize">{channel}</span></div>
              <div className="pt-2 border-t"><p className="text-gray-500 mb-1">Message</p><p>{preview}</p></div>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setStep(2)}>Back</Button>
              <Button onClick={handleLaunch} disabled={launchMutation.isPending || createMutation.isPending}>
                Launch Campaign
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {toast && (
        <div className="fixed bottom-6 right-6 flex items-center gap-2 rounded-lg bg-green-600 px-4 py-3 text-white shadow-lg">
          <CheckCircle className="h-5 w-5" />
          {toast}
        </div>
      )}
    </div>
  )
}
